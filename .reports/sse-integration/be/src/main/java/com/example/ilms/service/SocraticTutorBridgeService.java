package com.example.ilms.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import com.example.ilms.client.FastApiSocraticChatClient;
import com.example.ilms.config.FastApiProperties;
import com.example.ilms.dto.common.PageResponse;
import com.example.ilms.dto.response.ApiResponse;
import com.example.ilms.dto.socratic.MessageFeedbackRequestDto;
import com.example.ilms.dto.socratic.SocraticChatStreamRequestDto;
import com.example.ilms.dto.socratic.SocraticSessionDetailDto;
import com.example.ilms.dto.socratic.SocraticSessionSidebarDto;
import com.example.ilms.dto.socratic.SocraticSessionSidebarDto.SessionUpdateRequest;

import reactor.core.Disposable;
import reactor.core.Disposables;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.example.ilms.exception.ErrorCode;
import reactor.core.publisher.Flux;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Service trung gian bên Spring Boot điều phối luồng Socratic Tutor Chat giữa
 * Frontend và FastAPI.
 * Dùng trực tiếp {@code ApiResponse<T>} và {@code PaginatedResponse<T>} có sẵn
 * của dự án.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SocraticTutorBridgeService {

    private final FastApiSocraticChatClient socraticChatClient;
    private final FastApiProperties properties;
    private final ObjectMapper objectMapper;

    /**
     * Phương án 1 (Reactive Flux): Chuyển tiếp trực tiếp từng frame SSE từ FastAPI
     * về Frontend.
     * Sử dụng trực tiếp 'authenticatedStudentId' truyền từ Controller (Thread chính).
     */
    public Flux<ServerSentEvent<String>> streamChatFlux(
            SocraticChatStreamRequestDto request,
            UUID authenticatedStudentId,
            String provider) {
        request.setStudent_id(authenticatedStudentId);
        return socraticChatClient.streamSocraticChat(request, provider, "STUDENT");
    }

    /**
     * Phương án 2 (Servlet SseEmitter): Bọc dòng chảy {@code Flux<ServerSentEvent<String>>} từ FastAPI
     * sang đối tượng {@link SseEmitter} chuẩn của Spring MVC.
     * Nhận 'authenticatedStudentId' được truyền tay trực tiếp từ THREAD CHÍNH của Controller.
     */
    public SseEmitter streamChatWithSseEmitter(
            SocraticChatStreamRequestDto request,
            UUID authenticatedStudentId,
            String provider) {
        SseEmitter emitter = new SseEmitter(properties.getSseTimeoutMillis());
        streamChatToEmitter(authenticatedStudentId, request, provider, emitter);
        return emitter;
    }

    /**
     * Truyền luồng trực tiếp vào đối tượng SseEmitter được cung cấp từ bên ngoài.
     * Dùng trực tiếp 'authenticatedStudentId', hoàn toàn KHÔNG phụ thuộc vào SecurityContextHolder.
     */
    public void streamChatToEmitter(
            UUID authenticatedStudentId,
            SocraticChatStreamRequestDto request,
            String provider,
            SseEmitter emitter) {
        request.setStudent_id(authenticatedStudentId);

        // Register cancellation before subscribe; callbacks can run synchronously.
        Disposable.Swap upstream = Disposables.swap();
        emitter.onCompletion(upstream::dispose);
        emitter.onTimeout(() -> {
            upstream.dispose();
            emitter.complete();
        });
        emitter.onError(error -> upstream.dispose());
        upstream.update(socraticChatClient
                .streamSocraticChat(request, provider, "STUDENT")
                .subscribe(event -> {
                    try {
                        SseEmitter.SseEventBuilder outgoing = SseEmitter.event();
                        if (StringUtils.hasText(event.event())) outgoing.name(event.event());
                        if (event.id() != null) outgoing.id(event.id());
                        if (event.retry() != null) outgoing.reconnectTime(event.retry().toMillis());
                        if (event.comment() != null) outgoing.comment(event.comment());
                        if (event.data() != null) outgoing.data(event.data());
                        if (event.data() != null || event.comment() != null) emitter.send(outgoing);
                    } catch (Exception sendError) {
                        upstream.dispose();
                        emitter.completeWithError(sendError);
                    }
                }, error -> {
                    log.warn("Socratic upstream stream failed: {}", error.getClass().getSimpleName());
                    try {
                        emitter.send(SseEmitter.event().name("error").data(objectMapper.writeValueAsString(Map.of(
                                "code", "SPRING_PROXY_ERROR",
                                "message", ErrorCode.SOCRATIC_STREAM_FAILED.getMessage(),
                                "recoverable", true,
                                "content_status", "INCOMPLETE"))));
                        emitter.complete();
                    } catch (Exception sendError) {
                        emitter.completeWithError(sendError);
                    }
                }, emitter::complete));
    }

    /**
     * Phương án 3 (Thread con bất đồng bộ CompletableFuture.runAsync):
     * Nhận trực tiếp 'authenticatedStudentId' đã lấy từ THREAD CHÍNH,
     * chạy trong ThreadPool mà không bao giờ gọi SecurityContextHolder.getContext().
     */
    public void callFastApiAndSaveDbAsync(
            UUID authenticatedStudentId,
            String message,
            UUID sessionId,
            String provider,
            SseEmitter emitter) {
        CompletableFuture.runAsync(() -> {
            try {
                SocraticChatStreamRequestDto request = SocraticChatStreamRequestDto.builder()
                        .session_id(sessionId)
                        .student_id(authenticatedStudentId)
                        .message(message)
                        .build();
                streamChatToEmitter(authenticatedStudentId, request, provider, emitter);
            } catch (Exception e) {
                log.error("Lỗi trong CompletableFuture khi gọi FastAPI SSE: {}", e.getMessage());
                emitter.completeWithError(e);
            }
        });
    }

    public ApiResponse<PageResponse<SocraticSessionSidebarDto>> listStudentSessions(
            UUID studentId,
            String subject,
            int pageNumber,
            int pageSize) {
        return socraticChatClient.listStudentSessions(studentId, subject, pageNumber, pageSize);
    }

    public ApiResponse<SocraticSessionDetailDto> getSessionDetail(
            UUID sessionId,
            UUID callerUserId,
            String callerRole) {
        return socraticChatClient.getSessionDetail(sessionId, callerUserId, callerRole);
    }

    public ApiResponse<SocraticSessionSidebarDto> updateSession(
            UUID sessionId,
            SessionUpdateRequest updateRequest,
            UUID studentId) {
        return socraticChatClient.updateSession(sessionId, updateRequest, studentId);
    }

    public ApiResponse<Map<String, Boolean>> deleteSession(
            UUID sessionId,
            UUID studentId) {
        return socraticChatClient.deleteSession(sessionId, studentId);
    }

    public ApiResponse<com.example.ilms.dto.socratic.SocraticSessionDetailDto.SocraticMessageItemDto> submitMessageFeedback(
            UUID messageId,
            MessageFeedbackRequestDto feedbackRequest,
            UUID studentId) {

        return socraticChatClient.submitMessageFeedback(messageId, feedbackRequest, studentId);
    }

}

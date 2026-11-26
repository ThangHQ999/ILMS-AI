package com.example.ilms.dto.socratic;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.UUID;

/**
 * Payload gửi từ Spring Boot sang FastAPI endpoint
 * {@code POST /api/v1/chat/socratic/stream}.
 * Ánh xạ 1-1 với {@code SocraticChatStreamRequest} trong
 * {@code app/schema/chat_sse_schema.py}.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class SocraticChatStreamRequestDto {
    private UUID session_id;
    private UUID student_id;
    private UUID teacher_id;
    @NotBlank(message = "Nội dung tin nhắn không được để trống")
    private String message;
    private String subject;
    private List<UUID> material_ids;

    private String active_canonical_code;
    private String activeProcess_id;
    private String activeExercise_id;
    private String forced_action;
    private UUID client_request_id;
    @PositiveOrZero
    private Long expected_state_version;
    @Builder.Default
    @Min(1)
    @Max(2)
    private Integer protocol_version = 1;
}
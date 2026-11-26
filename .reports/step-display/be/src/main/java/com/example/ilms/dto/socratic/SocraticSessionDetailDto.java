package com.example.ilms.dto.socratic;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

/**
 * DTO chi tiết của 1 phiên hội thoại Socratic kèm danh sách lịch sử tin nhắn
 * {@code socratic_chat_messages}.
 * Ánh xạ 1-1 với {@code SocraticChatSessionDetailResponse} và
 * {@code SocraticChatMessageResponse} bên FastAPI.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class SocraticSessionDetailDto {

    private UUID id;
    private UUID student_id;
    private UUID teacher_id;
    private String title;
    private String subject;
    private String active_canonical_code;
    private String active_process_id;
    private String active_exercise_id;
    private Integer current_step_number;
    private Boolean is_completed;
    private LocalDateTime created_at;
    private LocalDateTime updated_at;

    @Builder.Default
    private List<SocraticMessageItemDto> messages = Collections.emptyList();

    /**
     * DTO ánh xạ từng bản ghi tin nhắn trong bảng {@code socratic_chat_messages}.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class SocraticMessageItemDto {
        private UUID id;
        private UUID session_id;
        private String role;
        private String content;
        private Integer step_number_at_turn;
        private StepProgressDto step_progress;
        private List<String> referenced_chunk_ids;
        private List<String> referenced_node_ids;
        private String user_feedback;
        private String feedback_rating;
        private LocalDateTime created_at;
        private LocalDateTime updated_at;
    }

    @Data
    @NoArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class StepProgressDto {
        private String step_id;
        private String exercise_id;
        private Integer number;
        private Integer total;
        private String instruction;
        private Boolean completed;
    }

}
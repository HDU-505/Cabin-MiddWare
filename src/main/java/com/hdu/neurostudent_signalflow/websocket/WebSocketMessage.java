package com.hdu.neurostudent_signalflow.websocket;

import lombok.Data;

@Data
public class WebSocketMessage {
    private String id;
    private String from;
    private String to;
    private int type;
    private String content;

    // 扩展字段用于文件传输
    private String fileName;
    private Integer chunkIndex;
    private Integer totalChunks;

}

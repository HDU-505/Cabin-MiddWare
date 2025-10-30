package com.hdu.neurostudent_signalflow.websocket;

import lombok.Data;

@Data
public class WebSocketMessage {
    private String id;
    private String from;
    private String to;
    private int type;
    private String content;
}

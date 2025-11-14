package com.hdu.neurostudent_signalflow.utils.websocket;

import com.hdu.neurostudent_signalflow.utils.timestamp.TimestampSyncUtil;
import lombok.extern.slf4j.Slf4j;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/*
 *   服务器---》SDK发送命令的通道
 * */
@Slf4j
public class MindtoothWebSocketClient extends WebSocketClient {

    private static final long RECONNECT_INTERVAL = 10; // 重连间隔时间，单位：秒

    private ScheduledExecutorService executor;

    public MindtoothWebSocketClient(URI serverUri) {
        super(serverUri);
    }

    @Override
    public void onOpen(ServerHandshake arg0) {
        log.info("------ WebSocketClient onOpen ------");
        cancelReconnect(); // 连接成功时取消重连
    }

    @Override
    public void onClose(int arg0, String arg1, boolean arg2) {
        log.info("------ WebSocket onClose ------{}",arg1);
        scheduleReconnect(); // 连接关闭时进行重连
    }

    @Override
    public void onError(Exception arg0) {
        log.error("------ WebSocket onError ------{}",arg0);
        scheduleReconnect(); // 连接出错时进行重连
    }

    @Override
    public void onMessage(String response) {
//        log.info("-------- 接收到服务端数据： " + response + "--------");
//        if ("acquisition".equals(response)){
//            // 开始EEG数据采集
//            TimestampSyncUtil.resetTimestamp(System.currentTimeMillis());
//        }
    }

    private void scheduleReconnect() {
        executor = Executors.newSingleThreadScheduledExecutor();
        executor.schedule(this::reconnect, RECONNECT_INTERVAL, TimeUnit.SECONDS);
    }

    private void cancelReconnect() {
        if (executor != null && !executor.isShutdown()) {
            executor.shutdownNow();
        }
    }
}

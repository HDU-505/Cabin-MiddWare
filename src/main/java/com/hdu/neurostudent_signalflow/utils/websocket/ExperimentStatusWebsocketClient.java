package com.hdu.neurostudent_signalflow.utils.websocket;

import com.alibaba.fastjson.JSON;
import com.hdu.neurostudent_signalflow.experiment.ExperimentState;
import com.hdu.neurostudent_signalflow.utils.ApplicationRestart;
import com.hdu.neurostudent_signalflow.websocket.ExperimentStateMessage;
import lombok.extern.slf4j.Slf4j;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/*
 *   中间件服务器用于状态控制的类
 * */
@Slf4j
public class ExperimentStatusWebsocketClient extends WebSocketClient {

    private static final long RECONNECT_INTERVAL = 10; // 重连间隔时间，单位：秒

    private ScheduledExecutorService executor;

    public ExperimentStatusWebsocketClient(URI serverUri) {
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
        log.info("-------- 接收到服务端数据： " + response + "--------");
        // 如果实验状态变更成了结束，或者异常结束，则初始化中间件系统
        ExperimentStateMessage experimentStateMessage = JSON.parseObject(response,ExperimentStateMessage.class);

        if (experimentStateMessage != null && experimentStateMessage.getState() == ExperimentState.ERROR){
            // 重启系统
            ApplicationRestart.restart(new String[]{});
        }
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

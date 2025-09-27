package com.hdu.neurostudent_signalflow.config;

import com.hdu.neurostudent_signalflow.utils.websocket.ExperimentStatusWebsocketClient;
import com.hdu.neurostudent_signalflow.utils.websocket.MindtoothWebSocketClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

@Configuration
public class AppConfig {

//    @Bean
//    public BlockingQueue<String> stringBlockingQueue() {
//        return new LinkedBlockingQueue<>();
//    }

    private final String mindToothWsServerUrl = "ws://127.0.0.1:8888/websocket/w";
    private final String experimentStatusServerUrl = "ws://127.0.0.1:8888/websocket/experimentStatusServer?username=neurostudent_signalflow";

    @Bean
    @DependsOn("websocketServer")
    public MindtoothWebSocketClient webSocketClient() {
        try {
            MindtoothWebSocketClient webSocketClient =
                    new MindtoothWebSocketClient(new URI(mindToothWsServerUrl));
            ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();
            executor.schedule(() -> {
                webSocketClient.connect();
            }, 5, TimeUnit.SECONDS);
            return webSocketClient;
        } catch (URISyntaxException e) {
            e.printStackTrace();
        }
        return null;
    }

    @Bean
    @DependsOn("experimentStatusServer")
    public ExperimentStatusWebsocketClient experimentStatusServerClient() {
        try {
            ExperimentStatusWebsocketClient webSocketClient =
                    new ExperimentStatusWebsocketClient(new URI(experimentStatusServerUrl));
            ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();
            executor.schedule(() -> {
                webSocketClient.connect();
            }, 5, TimeUnit.SECONDS);
            return webSocketClient;
        } catch (URISyntaxException e) {
            e.printStackTrace();
        }
        return null;
    }
}
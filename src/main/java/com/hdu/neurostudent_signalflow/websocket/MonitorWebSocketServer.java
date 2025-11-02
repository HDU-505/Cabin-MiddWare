package com.hdu.neurostudent_signalflow.websocket;

import com.alibaba.fastjson.JSON;
import com.hdu.neurostudent_signalflow.config.AppIdentity;
import com.hdu.neurostudent_signalflow.config.ExperimentProperties;
import com.hdu.neurostudent_signalflow.experiment.ExperimentState;
import com.hdu.neurostudent_signalflow.experiment.ExperimentStateMachine;
import com.hdu.neurostudent_signalflow.monitor.ScreenMonitor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.PreDestroy;
import javax.websocket.*;
import javax.websocket.server.ServerEndpoint;
import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArraySet;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/*
*   监控服务器专用WebSocket服务器
* */
@ServerEndpoint("/websocket/monitorServer")
@Component
public class MonitorWebSocketServer {
    private static Logger logger = LoggerFactory.getLogger(MonitorWebSocketServer.class);

    // 静态变量，用来记录当前在线连接数
    private static int onlineCount = 0;

    // concurrent包的线程安全Set，用来存放每个客户端对应的MyWebSocket对象。
    private static CopyOnWriteArraySet<MonitorWebSocketServer> webSocketSet = new CopyOnWriteArraySet<>();

    // 存储客户端ID和对应的WebSocket对象
    private static ConcurrentHashMap<String, MonitorWebSocketServer> clientMap = new ConcurrentHashMap<>();

    // 实验状态监听器
    private static final ScreenMonitor.ScreenCaptureListener screenCaptureListener = new ScreenMonitor.ScreenCaptureListener() {
        @Override
        public void onScreenCaptured(byte[] imageData) {
            for (MonitorWebSocketServer client : webSocketSet) {
                try {
                    System.out.println("hello");
                    String clientId = client.clientId;
                    client.sendMessageByteData(imageData);
                } catch (IOException e) {
                    logger.error("[监控服务器]:向客户端:" + client.clientId  +" 发送屏幕捕获数据失败", e);
                }
            }
        }
    };

    static {
        ScreenMonitor.addScreenCaptureListener(screenCaptureListener);
    }

    // 与某个客户端的连接会话，需要通过它来给客户端发送数据
    private Session session;

    // 客户端ID
    private String clientId;

    public MonitorWebSocketServer() {
        // 注册监控状态监听器
        logger.info("启动实验状态控制服务器...");
    }

    /**
     * 连接建立成功调用的方法
     * @param session  可选的参数。session为与某个客户端的连接会话，需要通过它来给客户端发送数据
     * @throws IOException
     */
    @OnOpen
    public void onOpen(Session session) throws IOException {
        this.session = session;
        String queryString = session.getQueryString();

        Map<String, String> params = new ConcurrentHashMap<>();
        if (queryString != null) {
            params = Stream.of(queryString.split("&"))
                    .map(param -> param.split("="))
                    .collect(Collectors.toMap(param -> param[0], param -> param[1]));
        }

        String clientId = params.get("username");
        if (clientId == null) {
            clientId = "UnknownUser"; // 如果没有提供用户名，可以设置一个默认值
        }

        this.clientId = clientId;
        webSocketSet.add(this); // 加入set中
        clientMap.put(clientId, this); // 加入clientMap中
        addOnlineCount(); // 在线数加1
        logger.info("[监控服务器]:有新连接加入！当前在线人数为" + getOnlineCount());
        logger.info("[监控服务器]:新连接的客户端ID：" + clientId);
    }

    /**
     * 连接关闭调用的方法
     */
    @OnClose
    public void onClose() {
        webSocketSet.remove(this); // 从set中删除
        clientMap.remove(this.clientId); // 从clientMap中删除
        subOnlineCount(); // 在线数减1
        logger.info("[监控服务器]:" + this.clientId + "连接关闭！当前在线人数为" + getOnlineCount());
    }

    /**
     * 收到客户端消息后调用的方法
     * @param message 客户端发送过来的消息
     * @param session 可选的参数
     */
    @OnMessage
    public void onMessage(String message, Session session) {
        String clientId = this.clientId;
        logger.info("[监控服务器]:来自客户端用户" + clientId + "的消息:" + message);
        //只要是信息就要改变服务器状态
//        String[] messageArr = message.split(" ");
//        //修改数据信息
//        experimentId = messageArr[0];
//        ExperimentStatus.status = messageArr[1];

//      群发消息
//        for (MonitorWebSocketServer item : webSocketSet) {
//            try {
//                System.out.println("[状态控制服务器]:向客户端用户" + clientId + "发送消息:" + message);
//                item.sendMessage(message);
//            } catch (IOException e) {
//                e.printStackTrace();
//            }
//        }
    }

    /**
     * 发生错误时调用
     * @param session
     * @param error
     */
    @OnError
    public void onError(Session session, Throwable error) {
        logger.error("[监控服务器]:发生错误", error);
        error.printStackTrace();
    }

    /**
     * 这个方法与上面几个方法不一样。没有用注解，是根据自己需要添加的方法。
     * @param message
     * @throws IOException
     */
    public void sendMessage(String message) throws IOException {
        this.session.getBasicRemote().sendText(message);
    }

    public void sendMessageByteData(byte[] byteData) throws IOException {
        this.session.getBasicRemote().sendBinary(java.nio.ByteBuffer.wrap(byteData));
    }

    public static synchronized int getOnlineCount() {
        return onlineCount;
    }

    public static synchronized void addOnlineCount() {
        MonitorWebSocketServer.onlineCount++;
    }

    public static synchronized void subOnlineCount() {
        MonitorWebSocketServer.onlineCount--;
    }

    public static CopyOnWriteArraySet<MonitorWebSocketServer> getWebSocketSet() {
        return webSocketSet;
    }

    public static void setWebSocketSet(
            CopyOnWriteArraySet<MonitorWebSocketServer> webSocketSet) {
        MonitorWebSocketServer.webSocketSet = webSocketSet;
    }

    public Session getSession() {
        return session;
    }

    public void setSession(Session session) {
        this.session = session;
    }

    private String generateMonitorData() {
        ExperimentStateMessage experimentStateMessage = new ExperimentStateMessage(AppIdentity.getIdentity(), ExperimentProperties.experimentId,ExperimentProperties.state);
        return JSON.toJSONString(experimentStateMessage);

//        StringBuilder sb = new StringBuilder();
//        sb.append("experimentId").append("=");
//        sb.append(ExperimentProperties.experimentId).append("&");
//        sb.append("state").append("=");
//        sb.append(ExperimentProperties.state).append("&");
//        sb.append("experimentInfo").append("=");
//        sb.append(JSON.toJSONString(ExperimentProperties.experiment));
//        return sb.toString();
    }
}

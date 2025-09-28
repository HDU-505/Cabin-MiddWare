package com.hdu.neurostudent_signalflow.websocket;

import com.alibaba.fastjson.JSON;
import com.hdu.neurostudent_signalflow.config.ExperimentProperties;
import com.hdu.neurostudent_signalflow.experiment.ExperimentState;
import com.hdu.neurostudent_signalflow.experiment.ExperimentStateMachine;
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
 *   用于单台cabin的整体实验状态同步
 * */

@ServerEndpoint("/websocket/experimentStatusServer")
public class ExperimentStatusSocket {
    private static Logger logger = LoggerFactory.getLogger(ExperimentStatusSocket.class);

    // 静态变量，用来记录当前在线连接数
    private static int onlineCount = 0;

    // concurrent包的线程安全Set，用来存放每个客户端对应的MyWebSocket对象。
    private static CopyOnWriteArraySet<ExperimentStatusSocket> webSocketSet = new CopyOnWriteArraySet<>();

    // 存储客户端ID和对应的WebSocket对象
    private static ConcurrentHashMap<String, ExperimentStatusSocket> clientMap = new ConcurrentHashMap<>();

    // 实验状态监听器
    private final ExperimentStateMachine.StateChangeListener experimentStateLister = new ExperimentStateMachine.StateChangeListener() {
        private int maxRetryAttempts = 3;

        @Override
        public void onStateChange(ExperimentState oldState, ExperimentState newState) {
            int attempts = maxRetryAttempts;
            while (attempts > 0) {
                try {
                    sendMessage(generateExperimentMessage());
                    return; // 成功发送就退出
                } catch (IOException e) {
                    attempts--;
                    if (attempts == 0) {
                        logger.error("[状态控制服务器]:向客户端:" + clientId +" 发送实验状态失败", e);
                    } else {
                        try {
                            Thread.sleep(100); // 可以加个短延时
                        } catch (InterruptedException ignored) {}
                    }
                }
            }
        }

        @Override
        public void onError(ExperimentState errorState) {
            try {
                sendMessage(generateExperimentMessage());
            } catch (IOException e) {
                logger.error("[状态控制服务器]:向客户端:" + clientId +" 发送实验异常状态失败", e);
            }
        }
    };

    // 与某个客户端的连接会话，需要通过它来给客户端发送数据
    private Session session;

    // 客户端ID
    private String clientId;

    public ExperimentStatusSocket() {
        // 注册实验状态监听器
        ExperimentStateMachine.getInstance().addLister(experimentStateLister);
    }

    @PreDestroy
    private void cleanup() {
        // 注销实验状态监听器
        ExperimentStateMachine.getInstance().removeLister(experimentStateLister);
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
        logger.info("[状态控制服务器]:有新连接加入！当前在线人数为" + getOnlineCount());
        logger.info("[状态控制服务器]:新连接的客户端ID：" + clientId);

        // 连接建立后，发送当前实验状态给新连接的客户端
        this.sendMessage(ExperimentProperties.experimentId + "=" + ExperimentProperties.state);
    }

    /**
     * 连接关闭调用的方法
     */
    @OnClose
    public void onClose() {
        webSocketSet.remove(this); // 从set中删除
        clientMap.remove(this.clientId); // 从clientMap中删除
        subOnlineCount(); // 在线数减1
        logger.info("[状态控制服务器]:有一连接关闭！当前在线人数为" + getOnlineCount());
    }

    /**
     * 收到客户端消息后调用的方法
     * @param message 客户端发送过来的消息
     * @param session 可选的参数
     */
    @OnMessage
    public void onMessage(String message, Session session) {
        String clientId = this.clientId;
        logger.info("[状态控制服务器]:来自客户端用户" + clientId + "的消息:" + message);
        //只要是信息就要改变服务器状态
//        String[] messageArr = message.split(" ");
//        //修改数据信息
//        experimentId = messageArr[0];
//        ExperimentStatus.status = messageArr[1];

//      群发消息
//        for (ExperimentStatusSocket item : webSocketSet) {
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
        logger.error("[状态控制服务器]:发生错误", error);
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

    public static synchronized int getOnlineCount() {
        return onlineCount;
    }

    public static synchronized void addOnlineCount() {
        ExperimentStatusSocket.onlineCount++;
    }

    public static synchronized void subOnlineCount() {
        ExperimentStatusSocket.onlineCount--;
    }

    public static CopyOnWriteArraySet<ExperimentStatusSocket> getWebSocketSet() {
        return webSocketSet;
    }

    public static void setWebSocketSet(
            CopyOnWriteArraySet<ExperimentStatusSocket> webSocketSet) {
        ExperimentStatusSocket.webSocketSet = webSocketSet;
    }

    public Session getSession() {
        return session;
    }

    public void setSession(Session session) {
        this.session = session;
    }

    private String generateExperimentMessage() {
        StringBuilder sb = new StringBuilder();
        sb.append("experimentId").append("=");
        sb.append(ExperimentProperties.experimentId).append("&");
        sb.append("state").append("=");
        sb.append(ExperimentProperties.state).append("&");
        sb.append("experimentInfo").append("=");
        sb.append(JSON.toJSONString(ExperimentProperties.experiment));
        return sb.toString();
    }
}

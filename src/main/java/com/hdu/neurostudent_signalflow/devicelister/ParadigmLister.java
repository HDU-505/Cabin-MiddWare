package com.hdu.neurostudent_signalflow.devicelister;

import com.hdu.neurostudent_signalflow.adapter.LabelDeviceAdapter;
import com.hdu.neurostudent_signalflow.client.ExperimentClinet;
import com.hdu.neurostudent_signalflow.config.ExperimentProperties;
import com.hdu.neurostudent_signalflow.utils.timestamp.TimestampSyncUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Arrays;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

@Component
public class ParadigmLister extends DeviceLister {
    private static final Logger logger = LoggerFactory.getLogger(ParadigmLister.class);

    @Resource
    private ExperimentClinet experimentClinet;

    BlockingQueue<double[]> recvData;   //数据接收队列

    @Resource
    LabelDeviceAdapter labelDeviceAdapter;

    public ParadigmLister() {
        this.recvData = new LinkedBlockingQueue<>();
    }

    // 监听范式的标签数据
    @Override
    public void Lister() {
        logger.info("范式监听程序启动...");
        // 启动适配器
        labelDeviceAdapter.addData(recvData);
        labelDeviceAdapter.processDevice();
        // 创建一个ServerSocket监听指定端口
        ServerSocket serverSocket = null;
        try {
            serverSocket = new ServerSocket(7777);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        while (true) {
            // 接受客户端连接
            Socket clientSocket = null;
            try {
                clientSocket = serverSocket.accept();
                logger.info("Client connected to the server");
            } catch (IOException e) {
                logger.error("Error accepting client connection", e);
                continue;  // Continue to accept next client connection
            }
            logger.info("客户端连接到服务器");

            // 处理客户端连接
            Socket finalClientSocket = clientSocket;
            new Thread(() -> handleClient(finalClientSocket)).start();
        }
    }

    private void handleClient(Socket clientSocket) {
        logger.info("Handling client connection");
        try (BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
             PrintWriter out = new PrintWriter(new OutputStreamWriter(clientSocket.getOutputStream()), true)) {

            String inputLine;
            while ((inputLine = in.readLine()) != null) {
                logger.info("Received raw input: " + inputLine);

                String labelData = inputLine.trim();
                if (!labelData.isEmpty()) {
                    logger.info("Extracted Label Data: " + labelData);

                    // 获取当前的时间戳
//                    long currentTime = System.currentTimeMillis();
                    long currentTime = TimestampSyncUtil.getCurrentTimestamp();
                    double[] data = new double[2];
                    // 第一个值为时间戳，第二个值为标签数据
                    data[0] = currentTime;
                    data[1] = Double.parseDouble(labelData);

                    if (data[1] == 255.0){
                        // 结束标志，发送结束实验的请求
                        if (ExperimentProperties.experimentId != null)
                            experimentClinet.endExperiment(ExperimentProperties.experimentId);
                        else
                            throw new RuntimeException("实验ID为空，无法结束实验");
                    }

                    // 将数据存储到接收队列
                    recvData.add(data);
                    logger.info("Data added to recvData queue: [" + data[0] + ", " + data[1] + "]");

                    // 将数据追加写入文件
                    try (FileWriter writer = new FileWriter("label_data_comparison.txt", true)) { // "true" 表示追加模式
                        writer.write(Arrays.toString(data) + "  " +currentTime + "    " +System.lineSeparator() + "   "); // 将 EEG 数据转换为字符串并写入文件
                    } catch (IOException e) {
                        e.printStackTrace(); // 处理文件写入异常
                    }

                    // 向客户端发送确认消息（可选）
                    out.println("Data received: " + labelData);
                } else {
                    logger.warn("Invalid input format: " + inputLine);
                }
            }
        } catch (Exception e) {
            logger.error("Error handling client connection", e);
        } finally {
            try {
                clientSocket.close();
                logger.info("Client socket closed");
            } catch (Exception e) {
                logger.error("Error closing client socket", e);
            }
        }
    }


}

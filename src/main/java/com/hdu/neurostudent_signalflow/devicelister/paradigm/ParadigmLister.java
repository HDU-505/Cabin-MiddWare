package com.hdu.neurostudent_signalflow.devicelister.paradigm;

import com.hdu.neurostudent_signalflow.adapter.LabelDeviceAdapter;
import com.hdu.neurostudent_signalflow.client.ExperimentClinet;
import com.hdu.neurostudent_signalflow.config.ExperimentProperties;
import com.hdu.neurostudent_signalflow.config.ParadigmConfig;
import com.hdu.neurostudent_signalflow.devicelister.DeviceLister;
import com.hdu.neurostudent_signalflow.utils.timestamp.TimestampSyncUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Arrays;
import java.util.concurrent.*;

@Component
public class ParadigmLister extends DeviceLister {
    private static final Logger logger = LoggerFactory.getLogger(ParadigmLister.class);

    @Resource
    private ExperimentClinet experimentClinet;

    @Resource
    private ParadigmConfig paradigmConfig;

    @Resource
    private LabelDeviceAdapter labelDeviceAdapter;

    // 数据接收队列
    private final BlockingQueue<double[]> recvData = new LinkedBlockingQueue<>(1000);

    // 文件写入队列
    private BlockingQueue<double[]> fileQueue = null;

    // 客户端线程池
    private final ExecutorService clientPool = Executors.newCachedThreadPool();

    private volatile boolean running = true;
    private ServerSocket serverSocket;

    // 异步写文件线程
    private void startFileWriter() {
        Thread fileWriterThread = new Thread(() -> {
            try (FileWriter writer = new FileWriter("label_data_comparison.txt", true)) {
                while (running || !fileQueue.isEmpty()) {
                    double[] data = fileQueue.poll(100, TimeUnit.MILLISECONDS);
                    if (data != null) {
                        writer.write(Arrays.toString(data) + System.lineSeparator());
                        writer.flush();
                    }
                }
            } catch (Exception e) {
                logger.error("File write error", e);
            }
        });
        fileWriterThread.setDaemon(true);
        fileWriterThread.start();
    }

    @Override
    public void Lister() {
        if (!paradigmConfig.isEnabled()) {
            logger.info("范式监听未启用，跳过范式监听程序启动");
            return;
        }

        logger.info("范式监听程序启动...");
        labelDeviceAdapter.addData(recvData);
        labelDeviceAdapter.processDevice();
        if (paradigmConfig.isWrite2File()) {
            fileQueue = new LinkedBlockingQueue<>(1000);
            startFileWriter();
        }

        try {
            serverSocket = new ServerSocket(7777);
            while (running) {
                try {
                    Socket clientSocket = serverSocket.accept();
                    logger.info("Client connected: {}", clientSocket.getRemoteSocketAddress());
                    clientPool.submit(() -> handleClient(clientSocket));
                } catch (IOException e) {
                    if (running) {
                        logger.error("Error accepting client connection", e);
                    } else {
                        logger.info("服务器正在停止，accept 被中断");
                    }
                }
            }
        } catch (IOException e) {
            logger.error("ServerSocket 初始化失败", e);
        } finally {
            shutdown();
        }
    }

    private void handleClient(Socket clientSocket) {
        try (Socket socket = clientSocket;
             BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()), true)) {

            String inputLine;
            while ((inputLine = in.readLine()) != null) {
                String labelData = inputLine.trim();
                if (labelData.isEmpty()) {
                    logger.warn("Invalid input format: {}", inputLine);
                    continue;
                }

                double[] data = new double[2];
                data[0] = TimestampSyncUtil.getCurrentTimestamp();

                try {
                    data[1] = Double.parseDouble(labelData);
                } catch (NumberFormatException e) {
                    logger.warn("Invalid number format: {}", labelData);
                    continue;
                }

                if (data[1] == 255.0) {
                    if (ExperimentProperties.EXPERIMENT_ID != null)
                        experimentClinet.endExperiment(ExperimentProperties.EXPERIMENT_ID);
                    else
                        logger.error("实验ID为空，无法结束实验");
                }

                // 入队数据
                if (!recvData.offer(data, 100, TimeUnit.MILLISECONDS)) {
                    logger.warn("recvData 队列已满，丢弃数据: {}", Arrays.toString(data));
                }

                // 异步写文件
                if (paradigmConfig.isWrite2File() && !fileQueue.offer(data, 100, TimeUnit.MILLISECONDS)) {
                    logger.warn("fileQueue 队列已满，丢弃数据: {}", Arrays.toString(data));
                }

                // 向客户端发送确认
                out.println("Data received: " + labelData);
            }
        } catch (Exception e) {
            logger.error("Error handling client: {}", clientSocket.getRemoteSocketAddress(), e);
        }
    }

    // 停止服务器
    public void shutdown() {
        running = false;
        try {
            if (serverSocket != null && !serverSocket.isClosed()) {
                serverSocket.close();
            }
        } catch (IOException e) {
            logger.error("Error closing server socket", e);
        }
        clientPool.shutdown();
        try {
            if (!clientPool.awaitTermination(5, TimeUnit.SECONDS)) {
                clientPool.shutdownNow();
            }
        } catch (InterruptedException e) {
            clientPool.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}

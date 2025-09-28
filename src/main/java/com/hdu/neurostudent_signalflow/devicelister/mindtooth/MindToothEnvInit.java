package com.hdu.neurostudent_signalflow.devicelister.mindtooth;

import com.hdu.neurostudent_signalflow.config.MindToothProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.Resource;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

/*
*   功能：监听程序开始前的SDK及LSL-python流初始化
* */
@Component
public class MindToothEnvInit implements Runnable{
    private static final Logger logger = LoggerFactory.getLogger(MindToothEnvInit.class);

    // 用于存储启动的外部进程
    private List<Process> processes = new ArrayList<>();
    private Object lock = new Object();

    @Resource
    private MindToothProperties mindToothProperties;    //mindtooth配置类

    @Resource
    private MindToothStateMachine mindToothStateMachine;

    private String MINDTOOTH_PYTHON_PATH;
    private String MINDTOOTH_SDK_PATH;
    private int MAX_RETRY_COUNT;

    private int pythonRetryCount = 0;
    private int sdkRetryCount = 0;

    @PostConstruct
    private void init() {
        this.MINDTOOTH_PYTHON_PATH = mindToothProperties.getPython_path();
        this.MINDTOOTH_SDK_PATH = mindToothProperties.getSdk_path();
        this.MAX_RETRY_COUNT = mindToothProperties.getMax_retry_count();
    }

    @Override
    public void run() {
        logger.info("mindtooth硬件环境初始化...");
        // 添加关闭钩子
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("JVM 关闭，正在关闭所有相关的外部进程...");
            for (Process process : processes) process.destroy();
        }));

        // 启动线程分别执行 initStream() 和 startSDK()
        Thread initStreamThread = new Thread(this::initStream);
        Thread startSDKThread = new Thread(this::startSDK);
        // 启动线程
        initStreamThread.start();
        startSDKThread.start();
        // 等待线程完成
        try {
            initStreamThread.join();
            startSDKThread.join();
        } catch (InterruptedException e) {
            logger.error("mindtooth初始化线程等待失败", e);
        }
    }

    // 启动mindtooth的python操作程序
    public void initStream(){
        logger.info("mindtooth-python操作程序启动...");
        while (pythonRetryCount < MAX_RETRY_COUNT) {
            try {
                // 指定可执行文件的路径
                ProcessBuilder processBuilder = new ProcessBuilder(MINDTOOTH_PYTHON_PATH);

                // 将标准错误流合并到标准输出流
                processBuilder.redirectErrorStream(true);

                // 启动外部应用程序
                Process process = processBuilder.start();
                synchronized (lock) {
                    processes.add(process);
                }
                // 读取外部应用程序的输出流
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                String line;
                while ((line = reader.readLine()) != null) {
                    logger.info("mindtooth python output: {}",line);
                }

                // 等待外部应用程序退出
                int exitCode = process.waitFor();
                System.out.println("External application exited with code: " + exitCode);
                if (exitCode != 0) {
                    logger.error("mindtooth-python操作程序启动失败，退出代码: " + exitCode);
                    return ;
                }
                pythonRetryCount++;
            } catch (IOException | InterruptedException e) {
                logger.error("mindtooth-python操作程序启动失败...");
                e.printStackTrace();
                if (pythonRetryCount < MAX_RETRY_COUNT) {
                    pythonRetryCount++;
                } else {
                    logger.error("mindtooth-python操作程序启动失败，已达到最大重试次数");
                }
            }
        }
        logger.error("mindtooth-python操作程序启动失败，已达到最大重试次数");
    }

    // 启动mindtooth的SDK
    public void startSDK(){
        logger.info("mindtooth-SDK启动...");
        while (sdkRetryCount < MAX_RETRY_COUNT) {
            try {
                // 指定可执行文件的路径
                ProcessBuilder processBuilder = new ProcessBuilder(MINDTOOTH_SDK_PATH);
                // 启动外部应用程序
                Process process = processBuilder.start();
                synchronized (lock) {
                    processes.add(process);
                }

                // 读取外部应用程序的输出流
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                String line;
                while ((line = reader.readLine()) != null) {
                    logger.info("SDK output: {}", line);

                }
                // 等待外部应用程序退出
                int exitCode = process.waitFor();
                System.out.println("SDK External application exited with code: " + exitCode);
                if (exitCode != 0) {
                    logger.error("mindtooth-SDK启动失败，退出代码: " + exitCode);
                    return ;
                }
                sdkRetryCount++;
            } catch (IOException | InterruptedException e) {
                logger.error("mindtooth-SDK启动失败... \n {}",e.getMessage());
                sdkRetryCount++;
            }
        }
        logger.error("mindtooth-SDK启动失败，已达到最大重试次数");
    }

    public void shutdown() {
        logger.info("mindtooth-SDK及Python操作程序关闭...");

        // 关闭 Python 操作程序
        for (Process process : processes) {
            try {
                // 发送退出命令或者强制杀掉 Python 进程
                process.destroyForcibly();
            } catch (Exception e) {
                logger.error("mindtooth-Python操作程序关闭失败...", e);
            }
        }

        // 关闭 SDK
        try {
            // 使用 taskkill 命令强制关闭 SDK 进程
            ProcessBuilder processBuilder = new ProcessBuilder("taskkill", "/f", "/im", "eegAmpController.exe");
            Process process = processBuilder.start();
            int exitCode = process.waitFor();
            logger.info("SDK application exited with code: " + exitCode);
        } catch (Exception e) {
            logger.error("[2-1-3]:mindtooth-SDK关闭失败...", e);
        } finally {
            // 清空进程列表
            processes.clear();
        }
    }

}

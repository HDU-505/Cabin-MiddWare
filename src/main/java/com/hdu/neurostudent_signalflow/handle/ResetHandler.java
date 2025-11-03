package com.hdu.neurostudent_signalflow.handle;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;

public class ResetHandler {

    private static final Logger logger = LoggerFactory.getLogger(ResetHandler.class);

    // 开发阶段时候的逻辑
    // 发生异常情况，重启本系统
    public static void restart(String[] args){
        // 通过运行时重启
        try {
            String java = System.getProperty("java.home") + "/bin/java";
            String classpath = System.getProperty("java.class.path");
            String mainClass = "com.hdu.NeuroStudentSignalFlowApplication"; // 替换为你的主类

            ProcessBuilder processBuilder = new ProcessBuilder(java, "-cp", classpath, mainClass);
            processBuilder.start();
        } catch (IOException e) {
            logger.error("Failed to restart application", e);
        }
        // 退出当前进程
        System.exit(1);
    }

    // 打包后的逻辑代码
//    public static void restart(String[] args) {
//        try {
//            // 获取 JAR 文件路径
//            String jarPath = new File(ResetHandler.class.getProtectionDomain().getCodeSource().getLocation().toURI()).getPath();
//
//            // 构建重启命令
//            ProcessBuilder processBuilder = new ProcessBuilder("java", "-jar", jarPath);
//
//            // 如果有需要传递的命令行参数
//            if (args != null) {
//                processBuilder.command().addAll(List.of(args));
//            }
//
//            // 启动新进程
//            Process process = processBuilder.start();
//            logger.info("Application restart initiated.");
//
//            // 可选：等待新进程启动完成
//            process.waitFor();
//        } catch (IOException | InterruptedException | java.net.URISyntaxException e) {
//            logger.error("Failed to restart application", e);
//        }
//
//        // 退出当前进程
//        System.exit(1);
//    }

}

package com.hdu.neurostudent_signalflow.handle;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ResetHandler {

    private static final Logger logger = LoggerFactory.getLogger(ResetHandler.class);

    // 开发阶段时候的逻辑
    // 发生异常情况，重启本系统
//    public static void restart(String[] args){
//        // 通过运行时重启
//        try {
//            Thread.sleep(2000); // 等待2秒钟，确保当前进程完全退出
//            String java = System.getProperty("java.home") + "/bin/java";
//            String classpath = System.getProperty("java.class.path");
//            String mainClass = "com.hdu.NeuroStudentSignalFlowApplication"; // 替换为你的主类
//
//            ProcessBuilder processBuilder = new ProcessBuilder(java, "-cp", classpath, mainClass);
//            processBuilder.start();
//        } catch (Exception e) {
//            logger.error("Failed to restart application", e);
//        }
//        // 退出当前进程
//        System.exit(1);
//    }

    // 打包后的逻辑代码
    public static void restart(String[] args) {
//        try {
//            Thread.sleep(2000);
//
//            // 获取当前 Java 命令
//            String javaHome = System.getProperty("java.home");
//            String javaBin = javaHome + File.separator + "bin" + File.separator + "java";
//
//            // 获取类路径
//            String classpath = System.getProperty("java.class.path");
//
//            // 获取主类名
//            String mainClass = "com.hdu.neurostudent_signalflow.NeuroStudentSignalFlowApplication";
//
//            // 构建命令
//            List<String> command = new ArrayList<>();
//            command.add(javaBin);
//            command.add("-cp");
//            command.add(classpath);
//            command.add(mainClass);
//
//            if (args != null) {
//                command.addAll(Arrays.asList(args));
//            }
//
//            ProcessBuilder processBuilder = new ProcessBuilder(command);
//            processBuilder.directory(new File(System.getProperty("user.dir")));
//
//            // 继承环境变量
//            processBuilder.inheritIO();
//
//            Process process = processBuilder.start();
//            logger.info("Application restart initiated using classpath");
//
//            // 不等待，直接退出
//            System.exit(0);
//
//        } catch (Exception e) {
//            logger.error("Failed to restart application", e);
//            System.exit(1);
//        }
        throw new RuntimeException("Restart functionality is disabled for safety reasons.");
    }

}

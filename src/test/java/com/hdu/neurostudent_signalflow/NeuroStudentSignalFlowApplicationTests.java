package com.hdu.neurostudent_signalflow;

import com.hdu.neurostudent_signalflow.devicelister.mindtooth.MindToothDeviceLister;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import java.io.IOException;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

@SpringBootTest
class NeuroStudentSignalFlowApplicationTests {


    BlockingQueue<String> sendQueue = new ArrayBlockingQueue<>(10);

//    @Resource
    MindToothDeviceLister mindToothDeviceLister;


    @Test
    void contextLoads() {
        try {
            // 指定可执行文件的路径
            String command = "SDK\\EegAmpApp\\eegAmpController.exe";

            // 启动外部应用程序
            Process process = Runtime.getRuntime().exec(command);

            // 等待应用程序退出
            process.waitFor();

            System.out.println("External application exited with code: " + process.exitValue());
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }


}

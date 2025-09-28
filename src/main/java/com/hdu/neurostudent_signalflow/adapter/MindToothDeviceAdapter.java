package com.hdu.neurostudent_signalflow.adapter;

import com.hdu.neurostudent_signalflow.config.MindToothProperties;
import com.hdu.neurostudent_signalflow.service.DataTransmitService;
import com.hdu.neurostudent_signalflow.thread.MindToothOperator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.concurrent.*;

/*
*   功能：mindtooth适配器类，用于消除mindtooth与统一数据标准之间的不同
* */
@Component
public class MindToothDeviceAdapter extends Device implements DeviceAdapter{
    private static final Logger logger = LoggerFactory.getLogger(MindToothDeviceAdapter.class);
    private boolean isRunning = true; // 控制线程运行的标志位

    @Resource
    private MindToothProperties mindToothProperties;    //mindtooth配置类

    @Resource
    private DataTransmitService dataTransmitService;    //统一数据转发类

    private BlockingQueue<String> sendQueue = new LinkedBlockingQueue<>();   //发送队列

    private ExecutorService mindtoothOperatorexecutorService = null;

    private MindToothOperator mindToothOperator = null;

    private int processThread = 5;  //处理线程数

    private ProcessThread[] processThreads = null;

    public MindToothDeviceAdapter() {
        super();
    }

    @PostConstruct
    public void init() {
        this.processThread = mindToothProperties.getProcessThread();
        this.mindtoothOperatorexecutorService = Executors.newFixedThreadPool(processThread);
        this.mindToothOperator = new MindToothOperator(sendQueue, mindToothProperties);
        processThreads = new ProcessThread[processThread];
        dataTransmitService.start();
    }

    @Override
    public void addData(Object data) {
        this.data = data;
    }   //设置接收队列

    @Override
    public void processDevice() {
        for (int i = 0;i < processThread;i++){
            BlockingDeque<double[]> processQueue = new LinkedBlockingDeque<>();
            ProcessThread processThread = new ProcessThread(i+1,processQueue);
            processThreads[i] = processThread;
            mindtoothOperatorexecutorService.execute(processThread);
        }
        new Thread(() -> {
            logger.info("MindToothDeviceAdatper 适配器数据处理程序启动...");
            int index = 0;
            try {
                while (isRunning) {
                    if (data == null) continue;
                    double[] singleData = ((BlockingDeque<double[]>) data).takeFirst();
                    index++;
                    index = index % processThread;
                    processThreads[index].queue.putLast(singleData);
                }
            } catch (InterruptedException e) {
                logger.error("MindToothDeviceAdatper 适配器数据处理程序被中断: {}", e.getMessage());
            }
        }).start();
    }

    private class ProcessThread implements Runnable{
        int threadId;
        BlockingDeque<double[]> queue;

        public ProcessThread(int threadId, BlockingDeque<double[]> queue) {
            this.threadId = threadId;
            this.queue = queue;
        }

        @Override
        public void run() {
            while (isRunning){
                try {
                    double[] data = queue.takeFirst();
                    mindToothOperator.EEGData2UnifyData(data);
                } catch (InterruptedException e) {
                    logger.error("MindToothDeviceAdatper.ProcessThread 线程 {} 被中断: {}", threadId, e.getMessage());
                }
            }
        }
    }

}

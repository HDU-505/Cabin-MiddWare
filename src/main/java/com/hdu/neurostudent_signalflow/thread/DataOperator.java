package com.hdu.neurostudent_signalflow.thread;

import com.hdu.neurostudent_signalflow.service.Impl.DataTransmitService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.concurrent.*;

/*
*   串口数据处理线程类
* */
@Component
public class DataOperator {
    private static final Logger logger = LoggerFactory.getLogger(DataOperator.class);

    private StringBuilder incompleteData = new StringBuilder();
    private BlockingQueue<String> queue;

    @Resource
    private DataTransmitService dataTransmitService;

    //任务线程池
    private ExecutorService executorService = Executors.newFixedThreadPool(2);

    //待发送的数据队列
    private BlockingQueue<String> sendQueue = new LinkedBlockingQueue<>();

    public void setQueue(BlockingQueue<String> queue) {
        this.queue = queue;
    }

    // 用于创建处理时间戳的线程池
    public void operatopr() {
        logger.info("串口数据时间戳线程池创建成功");
        for (int i = 0;i < 2;i++){
            executorService.execute(new JsonProcessor(sendQueue,queue));
        }
        handleSendQueue();
    }

    public void handleSendQueue(){
        dataTransmitService.setSendQueue(sendQueue);
        dataTransmitService.start();
    }
}
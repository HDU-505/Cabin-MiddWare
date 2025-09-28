package com.hdu.neurostudent_signalflow.thread;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.hdu.neurostudent_signalflow.adapter.ComDeviceAdapter;
import com.hdu.neurostudent_signalflow.service.DataTransmitService;
import com.hdu.neurostudent_signalflow.service.UnifyDataService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.Map;
import java.util.Queue;
import java.util.Set;
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
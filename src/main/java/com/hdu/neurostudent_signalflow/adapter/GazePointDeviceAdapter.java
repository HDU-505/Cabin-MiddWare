package com.hdu.neurostudent_signalflow.adapter;

import com.hdu.neurostudent_signalflow.service.DataTransmitService;
import com.hdu.neurostudent_signalflow.thread.GazepointOperator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.Queue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;

/*
*   功能：眼动仪适配器类，用于将眼动仪数据转换成统一格式要求
*
* */

@Component
public class GazePointDeviceAdapter extends Device implements DeviceAdapter{
    private static final Logger logger = LoggerFactory.getLogger(GazePointDeviceAdapter.class);

    //发送队列
    private BlockingQueue<String> sendQuue = new LinkedBlockingQueue<>();
    // 数据转发服务对象
    @Resource
    DataTransmitService dataTransmitService;
    // 添加数据
    @Override
    public void addData(Object data) {
        this.data = data;
    }

    // 数据处理函数
    @Override
    public void processDevice() {
        try{
            //创建线程池专门进行数据处理
            ExecutorService executorService = Executors.newFixedThreadPool(10);
            for (int i = 0;i < 10;i++){
                GazepointOperator gazepointOperator = new GazepointOperator((Queue<String>) data,sendQuue);
                executorService.execute(gazepointOperator);
            }

            // 数据转发
            dataTransmitService.setSendQueue(sendQuue);
            dataTransmitService.start();
        }catch (Exception e){
            e.printStackTrace();
            logger.error("[3-4-1]:gazepoint适配器数据转换出现异常...");
        }
    }
}

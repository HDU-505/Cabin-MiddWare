package com.hdu.neurostudent_signalflow.adapter;

import com.hdu.neurostudent_signalflow.service.DataTransmitService;
import com.hdu.neurostudent_signalflow.thread.LabelOperator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

/*
*   label设备适配器
* */
@Component
public class LabelDeviceAdapter extends Device implements DeviceAdapter{
    private static final Logger logger = LoggerFactory.getLogger(LabelDeviceAdapter.class);

    //发送队列
    private BlockingQueue<String> sendQuue = new LinkedBlockingQueue<>(1000);

    // 数据转发服务对象
    @Resource
    DataTransmitService dataTransmitService;

    @Override
    public void addData(Object data) {
        this.data = data;
    }

    @Override
    public void processDevice() {
        try{
            LabelOperator labelOperator = new LabelOperator((BlockingQueue<double[]>) data,sendQuue);
            Thread thread = new Thread(labelOperator);
            thread.start();

            // 数据转发
            dataTransmitService.setSendQueue(sendQuue);
            dataTransmitService.start();
        }catch (Exception e){
            e.printStackTrace();
            logger.error("label适配器数据转换出现异常...");
        }
    }
}

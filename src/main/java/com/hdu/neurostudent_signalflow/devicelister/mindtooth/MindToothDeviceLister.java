package com.hdu.neurostudent_signalflow.devicelister.mindtooth;

import com.hdu.neurostudent_signalflow.adapter.MindToothDeviceAdapter;
import com.hdu.neurostudent_signalflow.config.MindToothProperties;
import com.hdu.neurostudent_signalflow.devicelister.DeviceLister;
import com.hdu.neurostudent_signalflow.utils.websocket.MindtoothWebSocketClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.concurrent.BlockingDeque;
import java.util.concurrent.LinkedBlockingDeque;

/*
*   用于监听mindtooth的数据与阻抗值
* */
@Component
public class MindToothDeviceLister extends DeviceLister {
    private static final Logger logger = LoggerFactory.getLogger(MindToothDeviceLister.class);

    @Resource
    private MindToothProperties mindToothProperties;  //mindtooth配置类
    @Resource
    private MindToothDeviceAdapter mindToothDeviceAdatper;  //mindtooth适配器类
    @Resource
    private MindToothDataLister mindToothDataLister;    //mindtooth数据监听类
    @Resource
    private MindToothImpLister mindToothImpLister;  //mindtooth阻抗值监听类
    @Resource
    private MindToothEnvInit mindToothEnvInit;  //mindtooth环境初始化类
    @Resource
    private MindtoothWebSocketClient mindtoothWebSocketClient;  //mindtooth命令转发websocket客户端
    //创建一个队列，用于存储获取的数据，
    private BlockingDeque<double[]> recvData = new LinkedBlockingDeque<>(); //接收队列

    @Override
    public void Lister() {
        super.Lister();
        if (!mindToothProperties.isEnabled()) {
            logger.info("Mindtooth未启用，监听程序不启动");
            return ;
        }
        logger.info("[2]:mindtooth初始化程序启动...");
        //启动适配器
        mindToothDeviceAdatper.addData(recvData);
        //启动适配器处理过程
        mindToothDeviceAdatper.processDevice();
        //另起一个线程启动环境
        new Thread(mindToothEnvInit).start();

        mindToothDataLister.setRecQueue(recvData);
        mindToothDataLister.setMindToothDeviceAdatper(mindToothDeviceAdatper);
        mindToothImpLister.setRecQueue(recvData);
        //启动数据监听程序
        new Thread(mindToothDataLister).start();
        //启动阻抗值监听程序
        new Thread(mindToothImpLister).start();
    }
}

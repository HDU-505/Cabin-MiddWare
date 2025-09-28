package com.hdu.neurostudent_signalflow.devicelister;

import com.hdu.neurostudent_signalflow.devicelister.mindtooth.MindToothDeviceLister;
import com.hdu.neurostudent_signalflow.devicelister.paradigm.ParadigmLister;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;


/*
*   监听器初始化程序
* */
@Component
public class ListerInit implements CommandLineRunner {
    private static final Logger logger = LoggerFactory.getLogger(ListerInit.class);

    @Resource
    GazepointDeviceLister gazepointDeviceLister;
    @Resource
    CommDeviceLister commDeviceLister;
    @Resource
    MindToothDeviceLister mindToothDeviceLister;
    @Resource
    ParadigmLister paradigmLister;

    @Override
    public void run(String... args) {
        logger.info("监听初始化程序正常启动");
//        // 启动眼动仪监听设备
//        Thread gazeThread = new Thread(gazepointDeviceLister);
//        gazeThread.start();
//        //启动串口监听程序
//        Thread commThread = new Thread(commDeviceLister);
//        commThread.start();
        //启动MindTOOTH监听程序
        Thread mindtoothThread = new Thread(mindToothDeviceLister);
        mindtoothThread.start();
        //启动label监听程序
//        Thread paradigmThread = new Thread(paradigmLister);
//        paradigmThread.start();
    }

}

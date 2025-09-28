package com.hdu.neurostudent_signalflow.destory;

import com.hdu.neurostudent_signalflow.devicelister.mindtooth.MindToothEnvInit;
import org.springframework.stereotype.Component;

import javax.annotation.PreDestroy;
import javax.annotation.Resource;

@Component
public class SystemDestory {

    @Resource
    private MindToothEnvInit mindToothEnvInit;
    // 在系统关闭前进行一些关闭操作
    @PreDestroy
    public void systemDestory(){
        // 将redis中的数据全都清空
        System.out.println("进行销毁操作");
        mindToothEnvInit.shutdown();
    }
}

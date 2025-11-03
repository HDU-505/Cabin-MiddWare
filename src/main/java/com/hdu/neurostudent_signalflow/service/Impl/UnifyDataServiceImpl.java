package com.hdu.neurostudent_signalflow.service.Impl;

import com.alibaba.fastjson2.JSON;
import com.hdu.neurostudent_signalflow.entity.UnifyData;
import com.hdu.neurostudent_signalflow.service.UnifyDataService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.Queue;

@Component
@Scope("prototype")
public class UnifyDataServiceImpl implements UnifyDataService {
    private static final Logger logger = LoggerFactory.getLogger(UnifyDataServiceImpl.class);

    private UnifyData data;

//    @Resource



    @Override
    public void operatorM(Map<String, Object> map) {
        Map<String,Object> header = (Map<String, Object>) map.get("header");
        data = new UnifyData((String) header.get("device_id"),(String)header.get("protocol_version"),header.get("sampling_rate")+"",header.get("channels")+"",(String)header.get("type"));
    }

    @Override
    public void operatorD(Map<String, Object> map,String timestamp) {
        List<Double> data = (List<Double>) map.get("data");
        // 给数据结构添加时间戳
        this.data.setTimeStamp(timestamp);
        this.data.data = data;
    }

    //  后续处理
    @Override
    public void handle(Queue<String> sendQueue) {
        String jsonData = JSON.toJSONString(data);
        //数据转存
        sendQueue.offer(jsonData);
    }
}

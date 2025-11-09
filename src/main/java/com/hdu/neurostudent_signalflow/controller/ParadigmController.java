package com.hdu.neurostudent_signalflow.controller;

import com.hdu.neurostudent_signalflow.entity.ParadigmTouchScreen;
import com.hdu.neurostudent_signalflow.service.ParadigmService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.Resource;
import java.util.List;

@RestController
@RequestMapping("/paradigm")
public class ParadigmController {
    private static final Logger logger = LoggerFactory.getLogger(ParadigmController.class);

    @Resource
    ParadigmService paradigmService;

    /*
     *   接收work station传来的范式文件
     * */
    @PostMapping("/forwardParadigm")
    public boolean forwardParadigm(@RequestPart("cover") MultipartFile cover,
                                   @RequestPart("paradigm") MultipartFile paradigm) {
        if (cover == null || paradigm == null) {
            logger.error("Received null file in forwardParadigm");
            return false;
        }
        logger.info("Received cover file: " + cover.getOriginalFilename() + ", size: " + cover.getSize());
        return paradigmService.cacheFile(cover, paradigm);
    }

    /*
     *   接受work station传来的范式信息
     * */
    @PostMapping("/forwardParadigmInfo")
    public boolean forwardParadigmInfo(@RequestBody ParadigmTouchScreen paradigmTouchScreen){
        // 处理逻辑
        logger.info("Received paradigm info: " + paradigmTouchScreen.toString());
        return paradigmService.storeFile(paradigmTouchScreen);
    }

    /*
     *   获取所有的范式信息
     * */
    @GetMapping("/getAllParadigm")
    public List<ParadigmTouchScreen> getAllParadigm(){
        logger.info("Fetching all paradigm information");
        // 处理逻辑
        return paradigmService.getAllParadigm();
    }

    /*
     *  根据id获取范式信息
     * */
    @GetMapping("/getParadigmById/{id}")
    public ParadigmTouchScreen getParadigmById(@PathVariable String id){
        // 处理逻辑
        logger.info("Fetching paradigm by ID: " + id);
        return paradigmService.getParadigmById(id);
    }

    /*
     *   根据id选择此次实验的范式
     * */
    @GetMapping("/selectParadigmById/{id}")
    public boolean selectParadigmById(@PathVariable String id){
        logger.info("Selecting paradigm by ID: " + id);
        return paradigmService.selectParadigmById(id);
    }

    /*
     *   执行本次实验的范式
     * */
    @GetMapping("/executeParadigm/{experiment_id}")
    public boolean executeParadigm(@PathVariable String experiment_id){
        logger.info("Executing paradigm for experiment ID: " + experiment_id);
        return paradigmService.executeParadigm(experiment_id);
    }

}
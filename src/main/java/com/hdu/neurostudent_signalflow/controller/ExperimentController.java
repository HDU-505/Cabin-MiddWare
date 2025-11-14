package com.hdu.neurostudent_signalflow.controller;


import com.hdu.neurostudent_signalflow.entity.Experiment;
import com.hdu.neurostudent_signalflow.service.IExperimentService;
import com.hdu.neurostudent_signalflow.utils.response.R;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.List;

/**
 * <p>
 *  前端控制器
 * </p>
 *
 * @author DZL
 * @since 2024-05-28
 */
@RestController
@RequestMapping("/experiment")
@CrossOrigin
public class ExperimentController {

    @Autowired
    private IExperimentService experimentService;

    /*
    *   创建实验
    * */
    @PostMapping("/createExperiment")
    public R createExperiment(@RequestBody Experiment experiment) {
        //TODO 开始实验的标志，需要根据该标志进行数据缓存
        //创建实验处理过程
        String experiment_id = experimentService.createExperiment(experiment);
        return experiment_id != null ? R.ok().data("id", experiment_id) : R.error();
    }

    /*
    *   开始实验
    * */
    @GetMapping("/startExperiment/{experiment_id}")
    public R startExperiment(@PathVariable String experiment_id) {
        //开始实验处理过程
        System.out.println("Starting experiment with ID: " + experiment_id);
        boolean flag = experimentService.startExperiment(experiment_id);
        return flag ? R.ok() : R.error();
    }

    /*
     *   终止实验
     * */
    @GetMapping("/stopExperiment/{experiment_id}")
    public R stopExperiment(@PathVariable String experiment_id) {
        //开始实验处理过程
        System.out.println("Stoping experiment with ID: " + experiment_id);
        boolean flag = experimentService.stopExperiment(experiment_id);
        return flag ? R.ok() : R.error();
    }

}

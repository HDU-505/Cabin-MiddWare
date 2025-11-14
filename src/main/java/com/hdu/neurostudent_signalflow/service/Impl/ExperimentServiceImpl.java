package com.hdu.neurostudent_signalflow.service.Impl;

import com.hdu.neurostudent_signalflow.config.ExperimentProperties;
import com.hdu.neurostudent_signalflow.entity.Experiment;
import com.hdu.neurostudent_signalflow.experiment.ExperimentEvent;
import com.hdu.neurostudent_signalflow.experiment.ExperimentStateMachine;
import com.hdu.neurostudent_signalflow.service.IExperimentService;
import com.hdu.neurostudent_signalflow.utils.ExperimentStatus;
import com.hdu.neurostudent_signalflow.utils.IdGenerator;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * <p>
 *  服务实现类
 * </p>
 *
 * @author DZL
 * @since 2024-05-28
 */
@Service
public class ExperimentServiceImpl implements IExperimentService {

    private final ExperimentStateMachine experimentStateMachine = ExperimentStateMachine.getInstance();

    /*
    *   创建实验的处理函数
    *
    * */

    @Override
    public String createExperiment(Experiment experiment) {
        //首先判断信息是否完整
        if (experiment == null) return null;
        if (experiment.getName() == null
                || experiment.getAge() == null
                || experiment.getGender() == null
                || experiment.getParadigmId() == null)
            return null;

        //生成唯一性id
        experiment.setId(IdGenerator.generateExperimentId());

        //将实验id存储到全局变量中
        ExperimentProperties.experimentId = experiment.getId();
        ExperimentProperties.experiment = experiment;

        //修改实验状态为“等待”
        experimentStateMachine.handleEvent(ExperimentEvent.START_PREPARATION);
        return experiment.getId();
    }

    @Override
    public boolean startExperiment(String experimentId) {
        //判断实验id是否正确
        if (ExperimentProperties.experimentId.equals(experimentId) && experimentStateMachine.handleEvent(ExperimentEvent.START_EXPERIMENT)) {
                //设置实验开始时间
                ExperimentProperties.experiment.setStartTime(new Date());
                return true;

        }

        return false;
    }

    @Override
    public boolean stopExperiment(String experimentId) {
        return ExperimentProperties.experimentId.equals(experimentId) && experimentStateMachine.handleEvent(ExperimentEvent.RESET_EXPERIMENT);
    }

}

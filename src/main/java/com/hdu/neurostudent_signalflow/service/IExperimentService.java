package com.hdu.neurostudent_signalflow.service;



import com.hdu.neurostudent_signalflow.entity.Experiment;

import java.util.List;

/**
 * <p>
 *  服务类
 * </p>
 *
 * @author DZL
 * @since 2024-05-28
 */
public interface IExperimentService {

    String createExperiment(Experiment experiment);

    boolean startExperiment(String experimentId);

    boolean stopExperiment(String experimentId);
}

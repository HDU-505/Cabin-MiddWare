package com.hdu.neurostudent_signalflow.client;

import com.hdu.neurostudent_signalflow.config.FeignClientConfig;
import com.hdu.neurostudent_signalflow.utils.response.R;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

// 暂时弃用
@FeignClient(name = "service-work-station-8080", url = "http://127.0.0.1:8080", configuration = FeignClientConfig.class)
public interface ExperimentClinet {
    @GetMapping("/experiment/endExperiment/{experiment_id}")
    public R endExperiment(@PathVariable String experiment_id);
}

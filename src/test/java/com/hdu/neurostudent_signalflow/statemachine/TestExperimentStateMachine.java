package com.hdu.neurostudent_signalflow.statemachine;

import com.hdu.neurostudent_signalflow.experiment.ExperimentEvent;
import com.hdu.neurostudent_signalflow.experiment.ExperimentState;
import com.hdu.neurostudent_signalflow.experiment.ExperimentStateMachine;
import com.hdu.neurostudent_signalflow.websocket.ExperimentStatusSocket;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;

import javax.annotation.Resource;

@Controller
@RequestMapping("/test/experimentStateMachine")
public class TestExperimentStateMachine {
    private static Logger logger = LoggerFactory.getLogger(ExperimentStatusSocket.class);


    @GetMapping("/changeState/{event}")
    public String changeState(@PathVariable ExperimentEvent event) {
            ExperimentStateMachine experimentStateMachine = ExperimentStateMachine.getInstance();
        try {
            experimentStateMachine.handleEvent(event);
            return "State changed to: " + experimentStateMachine.getCurrentState();
        } catch (Exception e) {
            logger.error("Error changing state with event: " + event, e);
            return "Error changing state: " + e.getMessage();
        }
    }
}

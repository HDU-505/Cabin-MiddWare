package com.hdu.neurostudent_signalflow.experiment;

import com.hdu.neurostudent_signalflow.handle.EndHandler;
import com.hdu.neurostudent_signalflow.handle.ResetHandler;
import com.hdu.neurostudent_signalflow.handle.RunningHandler;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

@Component
@Slf4j
public class ApplicationAutoManager {
    @Resource
    private RunningHandler runningHandler;
    @Resource
    private EndHandler endHandler;

    private final ExperimentStateMachine.StateChangeListener stateChangeListener = new ExperimentStateMachine.StateChangeListener() {
        @Override
        public void onStateChange(ExperimentState oldState, ExperimentState newState,ExperimentEvent event) {
            handleStateChange(newState,event);
        }

        @Override
        public void onError(ExperimentState errorState,ExperimentEvent event) {
            handleStateChange(errorState,event);
        }
    };

    // 私有构造方法，防止外部实例化
    private ApplicationAutoManager() {
        ExperimentStateMachine.getInstance().addLister(stateChangeListener);
    }

    // 处理状态转变逻辑
    private void handleStateChange(ExperimentState state, ExperimentEvent event) {
        // 根据状态变化执行相应的操作
        switch (state) {
            case ERROR: {
                log.info("实验状态处于异常，重启系统");
                ResetHandler.restart(new String[]{});
                break;
            }
            case RUNNING: {
                log.info("实验状态处于运行期，执行运行期逻辑");
                runningHandler.handleRunningState();
                break;
            }
            case ENDED: {
                log.info("实验状态处于结束，执行结束逻辑");
                endHandler.handleEndState();
                break;
            }
            default: {
                log.info("实验状态处于{}，无特定处理逻辑", state);
                break;
            }
        }
    }
}
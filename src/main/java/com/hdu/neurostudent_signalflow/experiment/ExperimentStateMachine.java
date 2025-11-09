package com.hdu.neurostudent_signalflow.experiment;

import com.hdu.neurostudent_signalflow.config.ExperimentProperties;

import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

public class ExperimentStateMachine {

    private static final ExperimentStateMachine INSTANCE = new ExperimentStateMachine();
    private final AtomicReference<ExperimentState> currentState = new AtomicReference<>(ExperimentState.NOT_STARTED);

    // 状态转换表
    private final Map<ExperimentState, Map<ExperimentEvent, ExperimentState>> transitionTable = new HashMap<>();
    private final List<StateChangeListener> listeners = new ArrayList<>();

    private ExperimentStateMachine() {
        initTransitions();
        ExperimentProperties.state = ExperimentState.NOT_STARTED;
    }

    public static ExperimentStateMachine getInstance() {
        return INSTANCE;
    }

    private void initTransitions() {
        // NOT_STARTED 状态
        transitionTable.put(ExperimentState.NOT_STARTED, Map.of(
                ExperimentEvent.START_PREPARATION, ExperimentState.PREPARING,
                ExperimentEvent.ERROR_OCCURED, ExperimentState.ERROR
        ));

        // PREPARING 状态
        transitionTable.put(ExperimentState.PREPARING, Map.of(
                ExperimentEvent.START_EXPERIMENT, ExperimentState.RUNNING,
                ExperimentEvent.ERROR_OCCURED, ExperimentState.ERROR
        ));

        // RUNNING 状态
        transitionTable.put(ExperimentState.RUNNING, Map.of(
                ExperimentEvent.PAUSE_EXPERIMENT, ExperimentState.PAUSED,
                ExperimentEvent.END_EXPERIMENT, ExperimentState.ENDED,
                ExperimentEvent.ERROR_OCCURED, ExperimentState.ERROR
        ));

        // PAUSED 状态
        transitionTable.put(ExperimentState.PAUSED, Map.of(
                ExperimentEvent.RESUME_EXPERIMENT, ExperimentState.RUNNING,
                ExperimentEvent.END_EXPERIMENT, ExperimentState.ENDED,
                ExperimentEvent.ERROR_OCCURED, ExperimentState.ERROR
        ));

        // ENDED 状态（终态）
        transitionTable.put(ExperimentState.ENDED, Map.of(
                ExperimentEvent.ERROR_OCCURED, ExperimentState.ERROR,
                ExperimentEvent.RESET_EXPERIMENT, ExperimentState.NOT_STARTED
        ));

        // ERROR 状态（终态）
        transitionTable.put(ExperimentState.ERROR, Collections.emptyMap());
    }

    // 处理事件，返回是否状态改变成功
    public boolean handleEvent(ExperimentEvent event) {
        ExperimentState prevState;
        ExperimentState nextState;

        do {
            prevState = currentState.get();
            Map<ExperimentEvent, ExperimentState> possibleTransitions = transitionTable.getOrDefault(prevState, Map.of());
            nextState = possibleTransitions.get(event);

            if (nextState == null) {
                System.out.println("Invalid event " + event + " for state " + prevState);
                return false; // 无效事件
            }
        } while (!currentState.compareAndSet(prevState, nextState));

        ExperimentProperties.state = nextState; // 更新全局状态

        // 通知监听器状态变化
        for (StateChangeListener listener : listeners) {
            ExperimentState finalPrevState = prevState;
            ExperimentState finalNextState = nextState;
            new Thread(() -> {
                if (finalNextState == ExperimentState.ERROR) {
                    listener.onError(finalNextState,event);
                    return ;
                }
                listener.onStateChange(finalPrevState, finalNextState,event);
            }).start();
        }
        System.out.println("State changed: " + prevState + " → " + nextState);
        return true;
    }

    public ExperimentState getCurrentState() {
        return currentState.get();
    }

    public boolean isTerminalState() {
        return currentState.get() == ExperimentState.ENDED || currentState.get() == ExperimentState.ERROR;
    }

    public synchronized void addLister(StateChangeListener listener) {
        listeners.add(listener);
    }

    public synchronized void removeLister(StateChangeListener listener) {
        listeners.remove(listener);
    }

    public boolean reset() {
        ExperimentState prevState = currentState.get();
        if (prevState == ExperimentState.ENDED || prevState == ExperimentState.ERROR) {
            currentState.set(ExperimentState.NOT_STARTED);
            for (StateChangeListener listener : listeners) {
                listener.onStateChange(prevState, ExperimentState.ERROR, ExperimentEvent.ERROR_OCCURED);
            }
            System.out.println("State reset: " + prevState + " → NOT_STARTED");
            return true;
        }
        System.out.println("Reset not allowed from state: " + prevState);
        return false;
    }

    public interface StateChangeListener {
        void onStateChange(ExperimentState oldState, ExperimentState newState, ExperimentEvent event);     // 新增状态变化监听方法
        void onError(ExperimentState errorState, ExperimentEvent event);   // 新增错误处理方法
    }
}

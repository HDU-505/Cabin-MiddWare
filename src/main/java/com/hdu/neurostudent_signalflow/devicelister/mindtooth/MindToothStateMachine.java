package com.hdu.neurostudent_signalflow.devicelister.mindtooth;

import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
@Scope("singleton")
public class MindToothStateMachine {

    public enum State {
        INIT,           // 初始状态
        SCANNING,       // 扫描设备
        CONNECTING,     // 正在连接
        CONNECTED,      // 已连接
        CONFIGURING,    // 配置参数中
        READY,          // 准备就绪
        ACQUIRING,      // 采集中
        ERROR,          // 错误状态
        DISCONNECTED    // 已断开
    }

    public interface StateListener {
        void onStateChanged(State oldState, State newState);
        void onError(String message);
    }

    private final List<StateListener> listeners = new ArrayList<>();
    private State currentState = State.INIT;

    public synchronized State getCurrentState() {
        return currentState;
    }

    public synchronized void addListener(StateListener listener) {
        listeners.add(listener);
    }

    private synchronized void setState(State newState) {
        State oldState = this.currentState;
        this.currentState = newState;

        System.out.println("状态变化: " + oldState + " -> " + newState);

        // 通知监听器
        for (StateListener listener : listeners) {
            listener.onStateChanged(oldState, newState);
        }
    }

    // ---- 状态转换方法 ----
    public void startScan() {
        if (currentState == State.INIT || currentState == State.DISCONNECTED) {
            setState(State.SCANNING);
        } else {
            error("只能在初始/断开状态下扫描");
        }
    }

    public void connect() {
        if (currentState == State.SCANNING) {
            setState(State.CONNECTING);
        } else {
            error("只能在扫描完成后连接");
        }
    }

    public void onConnected() {
        if (currentState == State.CONNECTING) {
            setState(State.CONNECTED);
        } else {
            error("连接流程错误");
        }
    }

    public void configure() {
        if (currentState == State.CONNECTED) {
            setState(State.CONFIGURING);
        } else {
            error("未连接设备无法配置");
        }
    }

    public void ready() {
        if (currentState == State.CONFIGURING) {
            setState(State.READY);
        } else {
            error("必须配置完成后才可就绪");
        }
    }

    public void startAcquire() {
        if (currentState == State.READY) {
            setState(State.ACQUIRING);
        } else {
            error("未就绪无法采集数据");
        }
    }

    public void stopAcquire() {
        if (currentState == State.ACQUIRING) {
            setState(State.READY);
        } else {
            error("当前不是采集状态，无法停止");
        }
    }

    public void disconnect() {
        setState(State.DISCONNECTED);
    }

    public void error(String msg) {
        System.err.println("错误: " + msg);
        setState(State.ERROR);

        for (StateListener listener : listeners) {
            listener.onError(msg);
        }
    }
}

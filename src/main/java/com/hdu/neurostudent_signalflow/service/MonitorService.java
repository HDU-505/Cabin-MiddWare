package com.hdu.neurostudent_signalflow.service;

public interface MonitorService {
    void startScreenMonitor();
    void stopScreenMonitor();
    void startCameraMonitor();
    void stopCameraMonitor();
}

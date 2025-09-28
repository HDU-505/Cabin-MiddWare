package com.hdu.neurostudent_signalflow.entity;

import java.io.Serializable;
import java.util.Date;

/**
 * <p>
 * 
 * </p>
 *
 * @author DZL
 * @since 2024-05-28
 */
public class Experiment implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 实验主键
     */
    private String id;

    /**
     * 被试姓名
     */
    private String name;

    /**
     * 被试性别
     */
    private Integer gender;

    /**
     * 被试年龄
     */
    private Integer age;

    /**
     * 实验开始时间
     */
    private Date startTime;

    /**
     * 实验结束时间
     */
    private Date endTime;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 更新时间
     */
    private Date updateTime;

    /**
     * 范式id
     */
    private String paradigmId;

    /**
     * 操作员id
     */
    private String userId;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getGender() {
        return gender;
    }

    public void setGender(Integer gender) {
        this.gender = gender;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public Date getStartTime() {
        return startTime;
    }

    public void setStartTime(Date startTime) {
        this.startTime = startTime;
    }

    public Date getEndTime() {
        return endTime;
    }

    public void setEndTime(Date endTime) {
        this.endTime = endTime;
    }

    public Date getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }

    public Date getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(Date updateTime) {
        this.updateTime = updateTime;
    }

    public String getParadigmId() {
        return paradigmId;
    }

    public void setParadigmId(String paradigmId) {
        this.paradigmId = paradigmId;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    @Override
    public String toString() {
        return "Experiment{" +
            "id = " + id +
            ", name = " + name +
            ", gender = " + gender +
            ", age = " + age +
            ", startTime = " + startTime +
            ", endTime = " + endTime +
            ", createTime = " + createTime +
            ", updateTime = " + updateTime +
            ", paradigmId = " + paradigmId +
            ", userId = " + userId +
        "}";
    }
}

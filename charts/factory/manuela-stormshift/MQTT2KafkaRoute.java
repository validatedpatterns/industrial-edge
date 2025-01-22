package com.redhat.manuela.routes;

import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.component.kafka.KafkaConstants;
import org.apache.camel.model.OnCompletionDefinition;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class MQTT2KafkaRoute extends RouteBuilder {

    private static final Logger LOGGER = LoggerFactory.getLogger(MQTT2KafkaRoute.class);

    @PropertyInject("local.cluster.name")
    private String local_cluster_name;
    @PropertyInject("kafka.broker.uri")
    private String kafka_broker_uri;
    @PropertyInject("kafka.broker.topic.vibration")
    private String kafka_broker_topic_vibration;
    @PropertyInject("kafka.broker.topic.temperature")
    private String kafka_broker_topic_temperature;

    @PropertyInject("mqtt.broker.uri")
    private String mqtt_broker_uri;
    @PropertyInject("mqtt.broker.clientId")
    private String mqtt_broker_clientid;
    @PropertyInject("mqtt.broker.topic.vibration")
    private String mqtt_broker_topic_vibration;
    @PropertyInject("mqtt.broker.topic.temperature")
    private String mqtt_broker_topic_temperature;

    @Override
    public void configure() throws Exception {
        storeTemperatureInKafka();
        storeVibrationInKafka();
        //readTemperatureFromKafka();
        //readVibrationFromKafka();
    }

    private void storeTemperatureInKafka() {
        // This block is to extract the cluster name from our VP
        // localClusterDomain setting. Please see the config map.
        String temp = local_cluster_name;
        String delims="[ . ]+";
        String [] tokens = temp.split(delims);
        String cluster_name = tokens[1];

        from("paho:" + mqtt_broker_topic_temperature + "?brokerUrl=" + mqtt_broker_uri + "&clientId=" + mqtt_broker_clientid + "-temp")
            .log("Storing temperature message from [" + cluster_name + "] MQTT: ${body}")
            .setHeader(KafkaConstants.KEY, constant(cluster_name))
            //.setHeader(KafkaConstants.KEY, constant("sensor-temp"))
            .to("kafka:" + kafka_broker_topic_temperature + "?brokers=" + kafka_broker_uri)
            ;//.log("sent message: ${headers[org.apache.kafka.clients.producer.RecordMetadata]}");
    }

    private void storeVibrationInKafka() {
        // This block is to extract the cluster name from our VP
        // localClusterDomain setting. Please see the config map.
        String temp = local_cluster_name;
        String delims="[ . ]+";
        String [] tokens = temp.split(delims);
        String cluster_name = tokens[1];

        from("paho:" + mqtt_broker_topic_vibration + "?brokerUrl=" + mqtt_broker_uri + "&clientId=" + mqtt_broker_clientid + "-vibr")
            .log("Storing vibration message from [" + cluster_name + "] MQTT: ${body}")
            .setHeader(KafkaConstants.KEY, constant(cluster_name))
            // .setHeader(KafkaConstants.KEY, constant("sensor-temp"))
            .to("kafka:" + kafka_broker_topic_vibration + "?brokers=" + kafka_broker_uri)
            ;//.log("sent message: ${headers[org.apache.kafka.clients.producer.RecordMetadata]}");
    }

    private void readTemperatureFromKafka() {
        from("kafka:" + kafka_broker_topic_temperature + "?brokers=" + kafka_broker_uri)
            .log("Reading message from Kafka: ${body}")
            .log("    on the topic ${headers[kafka.TOPIC]}")
            .log("    on the partition ${headers[kafka.PARTITION]}")
            .log("    with the offset ${headers[kafka.OFFSET]}")
            .log("    with the key ${headers[kafka.KEY]}");
    }

    private void readVibrationFromKafka() {
        from("kafka:" + kafka_broker_topic_vibration + "?brokers=" + kafka_broker_uri)
            .log("Reading message from Kafka: ${body}")
            .log("    on the topic ${headers[kafka.TOPIC]}")
            .log("    on the partition ${headers[kafka.PARTITION]}")
            .log("    with the offset ${headers[kafka.OFFSET]}")
            .log("    with the key ${headers[kafka.KEY]}");
    }

    @Override
    public OnCompletionDefinition onCompletion() {
        return super.onCompletion();
    }
}

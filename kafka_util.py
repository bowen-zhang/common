from . import pattern


class EventConsumer(pattern.Worker):
  def __init__(self, kafka_consumer_builder, topic, group, *args, **kwargs):
    super().__init__(
        worker_name='Kafka Consumer: {0} ({1})'.format(topic, group), *args, **kwargs)
    self._kafka_consumer_builder = kafka_consumer_builder
    self._topic = topic
    self._group = group
    self._consumer = None

  def _on_start(self):
    self._consumer = self._kafka_consumer_builder(self._topic, self._group)

  def _on_stop(self):
    if self._consumer:
      self._consumer.close()
      self._consumer = None

  def _on_run(self):
    message_groups = self._consumer.poll(timeout_ms=500)
    for messages in message_groups.values():
      for message in messages:
        self.logger.debug('[{0}:{1}] Received message:\n{2}'.format(
            message.topic, self._group, message.value))
        try:
          self._on_event(message.value)
        except EventConsumerException as ex:
          self.logger.warn('[{0}:{1}] Failed to consume message: {2}'.format(
              message.topic, self._group, ex))

  def _on_event(self, event):
    raise NotImplementedError()


class EventConsumerException(Exception):
  pass

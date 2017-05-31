from django.db.models import signals

from .registry import model_documents
from .utils import delete, index

import logging
logger = logging.getLogger(__name__)

class ModelIndexer(object):
    """
    Class that automatically indexes any new or deleted mapped model objects.
    """

    def register_signal_handlers(self):
        """
        Register save and delete signal handler for mapped models. Also checks each ModelIndex for any additional signal handling that may be needed. 
        """

        for model_class, document_classes in model_documents.items():
            signals.post_save.connect(self.handle_save, sender=model_class, weak=False)
            signals.post_delete.connect(self.handle_delete, sender=model_class, weak=False)

            for document_class in document_classes:
                document_class.register_additional_signal_handlers(self)

    def handle_save(self, sender, instance, **kwargs):
        try:
            index(instance)
        except:
            logger.exception('Error indexing %s instance: %s', sender, instance)

    def handle_delete(self, sender, instance, **kwargs):
        try:
            delete(instance)
        except:
            logger.exception('Error deleting %s instance: %s', sender, instance)

    def handle_m2m_changed(self, sender, instance, action, **kwargs):
        if action == 'post_add' or action == 'post_clear' or action == 'post_clear':
            try:
                index(instance)
            except:
                logger.exception('Error indexing many to many change %s instance: %s', sender, instance)



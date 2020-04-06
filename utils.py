from app_4.models import *
import app_4.models
from inspect import isclass
from datetime import datetime

original_list_of_classes = [c for c in dir(app_4.models) if isclass(getattr(app_4.models,c))]
list_of_classes = original_list_of_classes.copy()
def creating_objects(list_of_classes = list_of_classes,min_value=0,max_value = 5):
    list_of_objects = []
    for class_name in list_of_classes:
        dict_of_attr = eval(f"{class_name}().__dict__")
        print(class_name)
        print(dict_of_attr)
        del dict_of_attr['_state']
        for i in range(min_value,max_value):
            for k in dict_of_attr:
                print(eval(f"{class_name}")._meta.get_field(f"{k}").get_internal_type())
                if eval(f"{class_name}")._meta.get_field(f"{k}").get_internal_type() == 'CharField':
                    dict_of_attr[k] = f"{k}_{i}"
                elif eval(f"{class_name}")._meta.get_field(f"{k}").get_internal_type() == 'EmailField':
                    dict_of_attr[k] = f"{k}{i}@gmail.com"
                elif eval(f"{class_name}")._meta.get_field(f"{k}").get_internal_type() == 'IntegerField':
                    dict_of_attr[k] = i
                elif eval(f"{class_name}")._meta.get_field(f"{k}").get_internal_type() == 'TextField':
                    dict_of_attr[k] = f"{k}_{i}"
                elif eval(f"{class_name}")._meta.get_field(f"{k}").get_internal_type() == 'DateField':
                    dict_of_attr[k] = f'200{i}-0{i+1}-0{i+2}'
                elif eval(f"{class_name}")._meta.get_field(f"{k}").get_internal_type() == 'OneToOneField':
                    dict_of_attr[k] = creating_objects([eval(f"{class_name}.{k}").field.remote_field.model.__name__ ],min_value=i,max_value=i+1)[0].id
                elif eval(f"{class_name}")._meta.get_field(f"{k}").get_internal_type() == 'ForeignKey':
                    dict_of_attr[k] = creating_objects([eval(f"{class_name}.{k}").field.remote_field.model.__name__ ],min_value=i,max_value=i+1)[0].id
                elif eval(f"{class_name}")._meta.get_field(f"{k}").get_internal_type() == 'ManyToManyField':
                    if eval(f"{class_name}.{k}").field.remote_field.through.__name__ not in original_list_of_classes:
                        creating_objects([eval(f"{class_name}.{k}").field.remote_field.through])
            list_of_objects.append(eval(f'{class_name}.objects.create(**{dict_of_attr})'))
    return list_of_objects

# creating_objects()


from devicehive import DeviceException
from devicehive import ApiResponseException


def test_list(test):

    def handle_connect(handler):
        test_id = test.generate_id('list-device')
        device_options = [{'id': '%s-1' % test_id,
                          'name': '%s-name-1' % test_id},
                          {'id': '%s-2' % test_id,
                           'name': '%s-name-2' % test_id}]
        devices = [handler.api.put_device(device_option['id'],
                                          device_option['name'])
                   for device_option in device_options]
        devices_list = handler.api.list_devices()
        assert len(devices_list) >= len(device_options)
        name = device_options[0]['name']
        devices_list = handler.api.list_devices(name=name)
        assert len(devices_list) == 1
        assert devices_list[0].name == name
        name_pattern = test.generate_id('list-not-exist')
        devices_list = handler.api.list_devices(name_pattern=name_pattern)
        assert not devices_list
        name_pattern = test_id + '%'
        devices_list = handler.api.list_devices(name_pattern=name_pattern)
        assert len(devices_list) == len(device_options)
        devices_list = handler.api.list_devices(name_pattern=name_pattern,
                                                sort_field='name',
                                                sort_order='ASC')
        assert devices_list[0].id() == device_options[0]['id']
        assert devices_list[1].id() == device_options[1]['id']
        devices_list = handler.api.list_devices(name_pattern=name_pattern,
                                                sort_field='name',
                                                sort_order='DESC')
        assert devices_list[0].id() == device_options[1]['id']
        assert devices_list[1].id() == device_options[0]['id']
        devices_list = handler.api.list_devices(name_pattern=name_pattern,
                                                sort_field='name',
                                                sort_order='ASC',
                                                take=1)
        assert len(devices_list) == 1
        devices_list = handler.api.list_devices(name_pattern=name_pattern,
                                                sort_field='name',
                                                sort_order='ASC',
                                                take=1, skip=1)
        assert devices_list[0].id() == device_options[1]['id']
        assert len(devices_list) == 1
        for device in devices:
            device.remove()

    test.run(handle_connect)


def test_get(test):

    def handle_connect(handler):
        device_id = test.generate_id('get-device')
        name = '%s-name' % device_id
        data = {'key': 'value'}
        handler.api.put_device(device_id, name=name, data=data)
        device = handler.api.get_device(device_id)
        assert device.id() == device_id
        assert device.name == name
        assert device.data == data
        assert isinstance(device.network_id, int)
        assert not device.is_blocked
        device.remove()
        device_id = test.generate_id('get-device-not-exist')
        try:
            handler.api.get_device(device_id)
            assert False
        except ApiResponseException as api_response_exception:
            # assert api_response_exception.code() == 404
            pass

    test.run(handle_connect)


def test_put(test):

    def handle_connect(handler):
        device_id = test.generate_id('put-device')
        device = handler.api.put_device(device_id)
        assert device.id() == device_id
        assert device.name == device_id
        assert not device.data
        assert isinstance(device.network_id, int)
        assert not device.is_blocked
        device.remove()
        name = '%s-name' % device_id
        data = {'key': 'value'}
        device = handler.api.put_device(device_id, name=name, data=data,
                                        is_blocked=True)
        assert device.id() == device_id
        assert device.name == name
        assert device.data == data
        assert isinstance(device.network_id, int)
        assert device.is_blocked
        device.remove()

    test.run(handle_connect)


def test_save(test):

    def handle_connect(handler):
        device_id = test.generate_id('save-device')
        device = handler.api.put_device(device_id)
        name = '%s-name' % device_id
        data = {'key': 'value'}
        device.name = name
        device.data = data
        device.is_blocked = True
        device.save()
        device = handler.api.get_device(device_id)
        assert device.id() == device_id
        assert device.name == name
        assert device.data == data
        assert isinstance(device.network_id, int)
        assert device.is_blocked
        device.remove()
        try:
            device.save()
            assert False
        except DeviceException:
            pass

    test.run(handle_connect)


def test_remove(test):

    def handle_connect(handler):
        device_id = test.generate_id('remove-device')
        remove_device = handler.api.put_device(device_id)
        remove_device.remove()
        assert not remove_device.id()
        assert not remove_device.name
        assert not remove_device.data
        assert not remove_device.network_id
        assert not remove_device.is_blocked
        remove_device = handler.api.put_device(device_id)
        device = handler.api.get_device(device_id)
        device.remove()
        try:
            device.remove()
            assert False
        except DeviceException:
            pass
        try:
            remove_device.remove()
            assert False
        except ApiResponseException as api_response_exception:
            # assert api_response_exception.code() == 404
            pass

    test.run(handle_connect)

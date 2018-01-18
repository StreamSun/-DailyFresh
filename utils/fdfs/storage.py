from django.conf import settings
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client

class FDFSStorage(Storage):
    """fdfs文件存储类"""
    def __init__(self,client=None,base_url=None):
        """初始化"""
        if client is None:
            self.client_conf = settings.FDFS_CLIENT_CONF
        if base_url is None:
            self.base_url = settings.FDFS_SERVER_URL

    def _open(self,name,mode='rb'):
        """获取文件"""
        pass

    def _save(self,name,content):
        """存储文件"""
        # name：选择上传文件的名称
        # content是一个File类的对象，这里是ImageFile类的对象
        # 创建client连接tracker-server
        client = Fdfs_client(self.client_conf)

        # 上传文件到fdfs服务器，返回值为group1/M00/00/00/wKhZhVpd4R-AapxFAABtR_KnVbE568.jpg
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # } if success else None
        res = client.upload_by_buffer(content.read())
        if  res is None or res['Status'] != 'Upload successed.':
            # 抛出异常
            raise Exception('fastdfs上传失败')
        file_id = res.get('Remote file_id')
        # 返回值存储在image字段内
        return file_id
    def exists(self, name):
        return False

    def url(self, name):
        return settings.FDFS_SERVER_URL + name



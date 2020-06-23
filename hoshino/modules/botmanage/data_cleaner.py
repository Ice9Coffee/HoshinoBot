import hoshino
from hoshino.typing import CommandSession

@hoshino.sucmd('清理数据')
async def clean_image(session: CommandSession):
    await hoshino.get_bot().clean_data_dir(self_id=session.event.self_id,
                                           data_dir='image')
    await session.send('Image 文件夹已清理')

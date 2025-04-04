from typing import cast

import nfc
from nfc.tag import Tag
from nfc.tag.tt3 import BlockCode, ServiceCode, Type3Tag
from nfc.tag.tt3_sony import FelicaStandard

SYSTEM_CODE = 0x809E

def read_data_block(tag: Type3Tag, service_code_number: int, block_code_number: int) -> bytearray:
	service_code = ServiceCode(service_code_number, 0x0B)
	block_code = BlockCode(block_code_number)
	read_bytearray = cast(bytearray, tag.read_without_encryption([service_code], [block_code]))
	print(read_bytearray)
	return read_bytearray


def get_student_id(tag: Type3Tag) -> str:
	student_id_bytearray = read_data_block(tag, 106, 0)
	return student_id_bytearray.decode()  # スライスで必要な部分だけ切り出す


def get_student_name(tag: Type3Tag) -> str:
	student_name_bytearray = read_data_block(tag, 106, 0)
	return student_name_bytearray.decode()	# スライスで必要な部分だけ切り出す


def on_connect(tag: Tag) -> bool:
	print("connected")
	if isinstance(tag, FelicaStandard) and SYSTEM_CODE in tag.request_system_code():  # カードがFeliCaでかつシステムコードが存在する場合
		tag.idm, tag.pmm, *_ = tag.polling(0xFE00)
		print(get_student_id(tag))
		print(get_student_name(tag))
	return True  # Trueを返しておくとタグが存在しなくなるまで待機される


def on_release(tag: Tag) -> None:
	print("released")


with nfc.ContactlessFrontend("usb") as clf:
	while True:
		clf.connect(rdwr={"on-connect": on_connect, "on-release": on_release})

from pyrogram import filters
from pyrogram import utils
from pyrogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from bot_client import bot, channel_id


def get_peer_type_new(peer_id: int) -> str:
	peer_id_str = str(peer_id)
	if not peer_id_str.startswith("-"):
		return "user"
	elif peer_id_str.startswith("-100"):
		return "channel"
	else:
		return "chat"


utils.get_peer_type = get_peer_type_new

sended_messages = []

users = {}
AFFIDAVIT2_buttons = ["I was denied access by the owner, the owner’s employee or agent or a person who claimed to be in control of the building", "I began to make the repairs but was interrupted by the owner, the owner's employee or agent or a person who claimed to be in control of the building and such individual ordered me to leave the premises"]


@bot.on_message(filters.command('start') & filters.private & filters.incoming)
async def start_message(_, message):
	if message.chat.id not in users:
		await message.reply(
			text='<b>Введите номер ОМО:</b>',
			reply_markup=ReplyKeyboardRemove()
			)
		users[message.chat.id] = {'state': 'send_omo'}

	else:
		state = users[message.chat.id]['state']
		if state in ['send_media', 'send_media_affidavit3.1', 'send_media_affidavit3.2']:
			await message.reply(
				text='<b>Введите номер OMO:</b>',
				reply_markup=ReplyKeyboardRemove()
				)
			users[message.chat.id]['state'] = 'send_omo'
			return

		await message.reply(
			text='<b>Выберите нужное:</b>',
			reply_markup=ReplyKeyboardMarkup([
				[KeyboardButton('AFFIDAVIT OF NO ACCESS')],
				[KeyboardButton('AFFIDAVIT OF REFUSED ACCESS')],
				[KeyboardButton('AFFIDAVIT OF COMPLETED')]],
				resize_keyboard=True
				)
			)
		users[message.chat.id]['state'] = 'menu'


@bot.on_message(filters.text & filters.private & filters.incoming)
async def text_handler(_, message):
	if message.chat.id not in users:
		await start_message(_, message)
		return

	state = users[message.chat.id]['state']

	if state == 'send_omo':
		users[message.chat.id]['OMO'] = message.text
		await start_message(_, message)

	elif state == 'menu':
		match message.text:
			case 'AFFIDAVIT OF NO ACCESS':
				await message.reply(
					text='I could not perform the work as directed because that portion of the premises in which the work performed was physically Inaccessible. The Inaccessibility was due to:',
					reply_markup=ReplyKeyboardRemove()
					)
				users[message.chat.id]['state'] = 'affidavit1'
				users[message.chat.id]['AFFIDAVIT'] = message.text

			case 'AFFIDAVIT OF REFUSED ACCESS':
				await message.reply(
					text=f'<b>Выберите нужное:</b>\n\n1) {AFFIDAVIT2_buttons[0]}\n\n2){AFFIDAVIT2_buttons[1]}',
					reply_markup=ReplyKeyboardMarkup([
						[KeyboardButton("1")],
						[KeyboardButton("2")]
						],
						resize_keyboard=True
						)
					)
				users[message.chat.id]['state'] = 'affidavit2'
				users[message.chat.id]['AFFIDAVIT'] = message.text

			case 'AFFIDAVIT OF COMPLETED':
				await message.reply(
					text='I have performed this work beginning on:',
					reply_markup=ReplyKeyboardRemove()
					)
				users[message.chat.id]['state'] = 'affidavit3'
				users[message.chat.id]['AFFIDAVIT'] = message.text

			case _:
				await message.reply(
					text='Выберите один из трех вариантов'
					)

	elif state == 'affidavit1':
		users[message.chat.id]['AFFIDAVIT_TEXT'] = f'I could not perform the work as directed because that portion of the premises in which the work performed was physically Inaccessible. The Inaccessibility was due to {message.text}'
		await message.reply(
			text='<b>Отправьте видео/фото:</b>',
			reply_markup=ReplyKeyboardRemove()
			)
		users[message.chat.id]['state'] = 'send_media'

	elif state == 'affidavit2':
		match message.text:
			case '1':
				await message.reply(
					text='<b>The Individual gave his/her name as:</b>\n\n<i>Click the button below if the individual refused to give his/her name</i>',
					reply_markup=ReplyKeyboardMarkup([[KeyboardButton('The individual refused to give his/her name')]],
						resize_keyboard=True,
						)
					)
				users[message.chat.id]['state'] = 'affidavit2.1.1'

			case "2":
				await message.reply(
					text='<b>The individual who prevented me from starting/completing the work:</b>\n\n<i>Click the button below if the individual refused to give his/her name</i>',
					reply_markup=ReplyKeyboardMarkup([[KeyboardButton('The individual refused to give his/her name')]],
						resize_keyboard=True,
						)
					)
				users[message.chat.id]['state'] = 'affidavit2.2.1'

			case _:
				await message.reply(
					text='Выберите один из двух вариантов'
					)

	elif state in ['affidavit2.1.1', 'affidavit2.2.1']:
		if state == 'affidavit2.1.1':
			users[message.chat.id]['AFFIDAVIT_TEXT'] = message.text if message.text == 'The individual refused to give his/her name' else f'The Individual gave his/her name as: {message.text}'
		else:
			users[message.chat.id]['AFFIDAVIT_TEXT'] = message.text if message.text == 'The individual refused to give his/her name' else f'The individual who prevented me from starting/completing the work: {message.text}'

		await message.reply(
			text='<b>The individual stated that his/her relationship to the building was:</b>\n\n<i>Click the button below if the individual refused to state his/her relationship to the building</i>',
			reply_markup=ReplyKeyboardMarkup([[KeyboardButton('The Individual refused to state his/her relationship to the building')]],
				resize_keyboard=True,
				)
			)
		users[message.chat.id]['state'] = 'affidavit2.1.2' if state == 'affidavit2.1.1' else 'affidavit2.2.2'

	elif state in ['affidavit2.1.2', 'affidavit2.2.2']:
		users[message.chat.id]['AFFIDAVIT_TEXT'] += f'\n{message.text}' if message.text == 'The Individual refused to state his/her relationship to the building' else f'\nThe individual stated that his/her relationship to the building was: {message.text}'
		await message.reply(
			text='<b>Description of individual (e.g., male/female, tall/short, dark/light hair):</b>',
			reply_markup=ReplyKeyboardRemove()
			)
		users[message.chat.id]['state'] = 'description2' if state == 'affidavit2.2.2' else 'description1'

	elif state == 'description1':
		users[message.chat.id]['AFFIDAVIT_TEXT'] += f'\nIndividual description: {message.text}'
		await message.reply(
			text='<b>Did the individual indicate work was completed?</b>',
			reply_markup=ReplyKeyboardMarkup([
				[KeyboardButton('Yes')],
				[KeyboardButton('No')]
				],
				resize_keyboard=True,
				)
			)
		users[message.chat.id]['state'] = 'work_complete'

	elif state == 'description2':
		users[message.chat.id]['AFFIDAVIT_TEXT'] += f'\nIndividual description: {message.text}'
		await message.reply(
			text='<b>Отправьте видео/фото:</b>',
			reply_markup=ReplyKeyboardRemove()
			)
		users[message.chat.id]['state'] = 'send_media'

	elif state == 'work_complete':
		match message.text:
			case 'Yes':
				users[message.chat.id]['AFFIDAVIT_TEXT'] += '\nThe individual indicated that the work was completed'

			case 'No':
				users[message.chat.id]['AFFIDAVIT_TEXT'] += '\nThe individual did not indicate that the work was completed'

			case _:
				await message.reply(
					text='Выберите один из двух вариантов'
					)
				return

		await message.reply(
			text='<b>Отправьте видео/фото:</b>',
			reply_markup=ReplyKeyboardRemove()
			)
		users[message.chat.id]['state'] = 'send_media'

	elif state == 'affidavit3':
		users[message.chat.id]['AFFIDAVIT_TEXT'] = f'I have performed this work beginning on {message.text} '
		await message.reply(
			text='<b>Отправьте видео/фото:</b>',
			reply_markup=ReplyKeyboardRemove()
			)
		users[message.chat.id]['state'] = 'send_media_affidavit3.1'

	elif state == 'affidavit3.3':
		users[message.chat.id]['AFFIDAVIT_TEXT'] += f'and completing it on {message.text}'
		await message.reply(
			text='<b>Отправьте видео/фото ПОСЛЕ:</b>',
			reply_markup=ReplyKeyboardRemove()
			)
		users[message.chat.id]['state'] = 'send_media_affidavit3.2'



@bot.on_message(filters.media_group & filters.private & filters.incoming)
async def media_group_handler(_, message):
	global sended_messages
	if message.media_group_id in sended_messages:
		return

	sended_messages.append(message.media_group_id)
	media_messages = await bot.get_media_group(
		chat_id=message.chat.id,
		message_id=message.id
		)

	if message.chat.id not in users:
		await start_message(_, message)
		return

	state = users[message.chat.id]['state']
	if state in ['send_media_affidavit3.1', 'send_media_affidavit3.2']:
		if state == 'send_media_affidavit3.1':
			users[message.chat.id]['media'] = [InputMediaPhoto(msg.photo.file_id) if msg.photo else InputMediaVideo(msg.video.file_id) for msg in media_messages]
			await message.reply(
				text='<b>and completing it on:</b>',
				reply_markup=ReplyKeyboardRemove()
				)
			users[message.chat.id]['state'] = 'affidavit3.3'

		elif state == 'send_media_affidavit3.2':
			users[message.chat.id]['media'] += [InputMediaPhoto(msg.photo.file_id) if msg.photo else InputMediaVideo(msg.video.file_id) for msg in media_messages]
			
			media_group = users[message.chat.id]['media']
			media_group[len(media_group) - 1].caption = f'''OMO: {users[message.chat.id]["OMO"]}\n{users[message.chat.id]["AFFIDAVIT"]}\n{users[message.chat.id]["AFFIDAVIT_TEXT"]}'''

			await bot.send_media_group(
				chat_id=channel_id,
				media=media_group
				)

			await message.reply(
				text='Отправлено в канал',
				reply_markup=ReplyKeyboardRemove()
				)

			await start_message(_, message)
		return

	if state != 'send_media':
		return

	media_group = []
	for msg in media_messages:
		if msg.photo:
			media_group.append(InputMediaPhoto(msg.photo.file_id))

		elif msg.video:
			media_group.append(InputMediaVideo(msg.video.file_id))

	media_group[len(media_group)-1].caption = f'''OMO: {users[message.chat.id]["OMO"]}
{users[message.chat.id]["AFFIDAVIT"]}
{users[message.chat.id]["AFFIDAVIT_TEXT"]}
'''

	await bot.send_media_group(
		chat_id=channel_id,
		media=media_group
		)

	await message.reply(
		text='Отправлено в канал',
		reply_markup=ReplyKeyboardRemove()
		)

	await start_message(_, message)

@bot.on_message((filters.photo | filters.video) & filters.private & filters.incoming)
async def media_handler(_, message):
	if message.chat.id not in users:
		await start_message(_, message)
		return

	state = users[message.chat.id]['state']

	if state in ['send_media_affidavit3.1', 'send_media_affidavit3.2']:
		if state == 'send_media_affidavit3.1':
			users[message.chat.id]['media'] = [InputMediaPhoto(message.photo.file_id) if message.photo else InputMediaVideo(message.video.file_id)]
			await message.reply(
				text='<b>and completing it on:</b>',
				reply_markup=ReplyKeyboardRemove()
				)
			users[message.chat.id]['state'] = 'affidavit3.3'

		else:
			users[message.chat.id]['media'].append(InputMediaPhoto(message.photo.file_id) if message.photo else InputMediaVideo(message.video.file_id))

			media_group = users[message.chat.id]['media']
			media_group[len(media_group) - 1].caption = f'''OMO: {users[message.chat.id]["OMO"]}\n{users[message.chat.id]["AFFIDAVIT"]}\n{users[message.chat.id]["AFFIDAVIT_TEXT"]}'''
			await bot.send_media_group(
				chat_id=channel_id,
				media=media_group
				)

			await message.reply(
				text='Отправлено в канал',
				reply_markup=ReplyKeyboardRemove()
				)

			await start_message(_, message)
		return

	if state != 'send_media':
		return

	caption = f'''OMO: {users[message.chat.id]["OMO"]}
{users[message.chat.id]["AFFIDAVIT"]}
{users[message.chat.id]["AFFIDAVIT_TEXT"]}
'''

	if message.photo:
		await bot.send_photo(
			chat_id=channel_id,
			photo=message.photo.file_id,
			caption=caption
			)

	elif message.video:
		await bot.send_video(
			chat_id=channel_id,
			video=message.video.file_id,
			caption=caption
			)

	await message.reply(
		text='Отправлено в канал',
		reply_markup=ReplyKeyboardRemove()		)

	await start_message(_, message)


bot.run()

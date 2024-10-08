from pyrogram import filters
from pyrogram import utils
from pyrogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from bot_client import bot, channel_id
from datetime import datetime


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
AFFIDAVIT2_buttons = [
    "I was denied access by the owner, the owner's employee or agent, or a person who claimed to be in control of the building",
    "I began to make the repairs but was interrupted by the owner, the owner's employee or agent, or a person who claimed to be in control of the building, and such individual ordered me to leave the premises"
]
AFFIDAVIT4 = """4) When I arrived at the work site on _____________________________,
<i>(date) (mm/dd/yy)</i>
I found that the work described in the OMO had been completed by others. I am entitled to a service charge of $ __________.

5) When I arrived at the work site on _____________________________,
<i>(date) (mm/dd/yy)</i>
I found a contractor, ___________________________________________________
(Contractor Company Name and worker at site)
at the site performing the same repairs I was directed to perform pursuant to OMO # ______. I am entitled to a service charge of $ __________.

6) When I arrived at the work site on _______________, I found that the
<i>(date) (mm/dd/yy)</i>
work described in the OMO was partially performed by others. I performed the remaining work described in the OMO and am entitled to a charge in the amount of $ _____________. (To be compensated for this work, the Contractor must attach an itemized invoice of work performed.)
"""

AFFIDAVIT4 = AFFIDAVIT4.replace('_', '＿')

@bot.on_message(filters.command('start') & filters.private & filters.incoming)
async def start_message(_, message):
    if message.chat.id not in users:
        await message.reply(
            text='<b>Enter OMO number:</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id] = {'state': 'send_omo'}

    else:
        state = users[message.chat.id]['state']
        if state in ['send_media', 'send_media_affidavit3.1', 'send_media_affidavit3.2']:
            await message.reply(
                text='<b>Enter OMO number:</b>',
                reply_markup=ReplyKeyboardRemove()
                )
            users[message.chat.id]['state'] = 'send_omo'
            return

        if state != 'send_omo':
            del users[message.chat.id]
            await start_message(_, message)
            return

        await message.reply(
            text='<b>Please select the required option:</b>',
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton('AFFIDAVIT OF NO ACCESS')],
                [KeyboardButton('AFFIDAVIT OF REFUSED ACCESS')],
                [KeyboardButton('AFFIDAVIT OF COMPLETED')],
                [KeyboardButton('AFFIDAVIT BY OTHERS')]],
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
        users[message.chat.id]['OMO'] = f'<code>{message.text}</code>'
        await start_message(_, message)

    elif state == 'menu':
        match message.text:
            case 'AFFIDAVIT OF NO ACCESS':
                await message.reply(
                    text='I could not perform the work as directed because that portion of the premises where the work was to be performed was physically inaccessible. The inaccessibility was due to:',
                    reply_markup=ReplyKeyboardRemove()
                    )
                users[message.chat.id]['state'] = 'affidavit1'
                users[message.chat.id]['AFFIDAVIT'] = f'<code>{message.text}</code>'

            case 'AFFIDAVIT OF REFUSED ACCESS':
                await message.reply(
                    text=f'<b>Please select one of the following options:</b>\n\n1) {AFFIDAVIT2_buttons[0]}\n\n2) {AFFIDAVIT2_buttons[1]}',
                    reply_markup=ReplyKeyboardMarkup([
                        [KeyboardButton("1")],
                        [KeyboardButton("2")]
                        ],
                        resize_keyboard=True
                        )
                    )
                users[message.chat.id]['state'] = 'affidavit2'
                users[message.chat.id]['AFFIDAVIT'] = f'<code>{message.text}</code>'

            case 'AFFIDAVIT OF COMPLETED':
                await message.reply(
                    text='I have performed this work beginning on:',
                    reply_markup=ReplyKeyboardRemove()
                    )
                users[message.chat.id]['state'] = 'affidavit3'
                users[message.chat.id]['AFFIDAVIT'] = f'<code>{message.text}</code>'

            case 'AFFIDAVIT BY OTHERS':
                await message.reply(
                    text=AFFIDAVIT4,
                    reply_markup=ReplyKeyboardMarkup([
                        [KeyboardButton('4')],
                        [KeyboardButton('5')],
                        [KeyboardButton('6')]
                        ],
                        resize_keyboard=True
                        )
                    )
                users[message.chat.id]['state'] = 'affidavit4_'
                users[message.chat.id]['AFFIDAVIT'] = f'<code>{message.text}</code>'

            case _:
                await message.reply(
                    text='You must choose one of the four options.'
                    )

    elif state == 'affidavit1':
        users[message.chat.id]['AFFIDAVIT_TEXT'] = f'I could not perform the work as directed because that portion of the premises where the work was to be performed was physically inaccessible. The inaccessibility was due to: <code>{message.text}</code>'
        await message.reply(
            text='<b>Send video/photo BEFORE:</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'send_media'

    elif state == 'affidavit2':
        match message.text:
            case '1':
                await message.reply(
                    text='<b>The individual gave his/her name as:</b>\n\n<i>Click the button below if the individual refused to give his/her name</i>',
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton('The individual refused to give his/her name')]],
                        resize_keyboard=True,
                        )
                    )
                users[message.chat.id]['state'] = 'affidavit2.1.1'

            case "2":
                await message.reply(
                    text='<b>Please provide the name of the individual who prevented me from starting/completing the work:</b>\n\n<i>Click the button below if the individual refused to give his/her name</i>',
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton('The individual refused to give his/her name')]],
                        resize_keyboard=True,
                        )
                    )
                users[message.chat.id]['state'] = 'affidavit2.2.1'

            case _:
                await message.reply(
                    text='You must choose one of the two options.'
                    )

    elif state in ['affidavit2.1.1', 'affidavit2.2.1']:
        if state == 'affidavit2.1.1':
            users[message.chat.id]['AFFIDAVIT_TEXT'] = message.text if message.text == '<code>The individual refused to give his/her name</code>' else f'The individual gave his/her name as: <code>{message.text}</code>'
        else:
            users[message.chat.id]['AFFIDAVIT_TEXT'] = message.text if message.text == '<code>The individual refused to give his/her name</code>' else f'The individual who prevented me from starting/completing the work: <code>{message.text}</code>'

        await message.reply(
            text='<b>The individual stated that his/her relationship to the building was:</b>\n\n<i>Click the button below if the individual refused to disclose his/her relationship to the building</i>',
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton('The individual refused to disclose his/her relationship to the building')]],
                resize_keyboard=True,
                )
            )
        users[message.chat.id]['state'] = 'affidavit2.1.2' if state == 'affidavit2.1.1' else 'affidavit2.2.2'

    elif state in ['affidavit2.1.2', 'affidavit2.2.2']:
        users[message.chat.id]['AFFIDAVIT_TEXT'] += f'\n{message.text}' if message.text == '<code>The individual refused to disclose his/her relationship to the building</code>' else f'\nThe individual stated that his/her relationship to the building was: <code>{message.text}</code>'
        await message.reply(
            text='<b>Description of individual (e.g., male/female, tall/short, dark/light hair):</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'description2' if state == 'affidavit2.2.2' else 'description1'

    elif state == 'description1':
        users[message.chat.id]['AFFIDAVIT_TEXT'] += f'\nIndividual description: <code>{message.text}</code>'
        await message.reply(
            text='<b>Did the individual indicate that the work was completed?</b>',
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton('Yes')],
                [KeyboardButton('No')]
                ],
                resize_keyboard=True,
                )
            )
        users[message.chat.id]['state'] = 'work_complete'

    elif state == 'description2':
        users[message.chat.id]['AFFIDAVIT_TEXT'] += f'\nIndividual description: <code>{message.text}</code>'
        await message.reply(
            text='<b>Send video/photo BEFORE:</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'send_media'

    elif state == 'work_complete':
        match message.text:
            case 'Yes':
                users[message.chat.id]['AFFIDAVIT_TEXT'] += '\nDid the individual indicate that the work was completed: <code>The individual indicated that the work was completed</code>'

            case 'No':
                users[message.chat.id]['AFFIDAVIT_TEXT'] += '\nDid the individual indicate that the work was completed: <code>The individual did not indicate that the work was completed</code>'

            case _:
                await message.reply(
                    text='You must choose one of the two options.'
                    )
                return

        await message.reply(
            text='<b>Send video/photo BEFORE:</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'send_media'

    elif state == 'affidavit3':
        users[message.chat.id]['AFFIDAVIT_TEXT'] = f'I have performed this work beginning on: <code>{message.text}</code>'
        await message.reply(
            text='<b>and completed it on:</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'affidavit3.3'

    elif state == 'affidavit3.3':
        users[message.chat.id]['AFFIDAVIT_TEXT'] += f' and completed it on: <code>{message.text}</code>'
        await message.reply(
            text='<b>Send video/photo BEFORE:</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'send_media'

    elif state == 'affidavit4_':
        match message.text:
            case '4':
                await message.reply(
                    text='When I arrived at the work site on:\n\n<i>Fill in with date. Date format (mm/dd/yy)</i>',
                    reply_markup=ReplyKeyboardRemove()
                    )
                users[message.chat.id]['state'] = 'affidavit4_4'

            case '5':
                await message.reply(
                    text='When I arrived at the work site on:\n\n<i>Fill in with date. Date format (mm/dd/yy)</i>',
                    reply_markup=ReplyKeyboardRemove()
                    )
                users[message.chat.id]['state'] = 'affidavit4_5'

            case '6':
                await message.reply(
                    text='When I arrived at the work site on:\n\n<i>Fill in with date. Date format (mm/dd/yy)</i>',
                    reply_markup=ReplyKeyboardRemove()
                    )
                users[message.chat.id]['state'] = 'affidavit4_6'

            case _:
                await message.reply(
                    text='You must choose one of the three options.'
                    )

    elif state == 'affidavit4_4':
        users[message.chat.id]['AFFIDAVIT_TEXT'] = f'When I arrived at the work site on: <code>{message.text}</code>, '
        message.text = '1'
        users[message.chat.id]['state'] = 'affidavit4.1'
        await text_handler(_, message)

    elif state == 'affidavit4_5':
        users[message.chat.id]['AFFIDAVIT_TEXT'] = f'When I arrived at the work site on: <code>{message.text}</code>, '
        message.text = '2'
        users[message.chat.id]['state'] = 'affidavit4.1'
        await text_handler(_, message)

    elif state == 'affidavit4_6':
        users[message.chat.id]['AFFIDAVIT_TEXT'] = f'When I arrived at the work site on: <code>{message.text}</code>, '
        message.text = '3'
        users[message.chat.id]['state'] = 'affidavit4.1'
        await text_handler(_, message)

    elif state == 'affidavit4.1':
        match message.text:
            case '1':
                users[message.chat.id]['AFFIDAVIT_TEXT'] += 'I found that the work described in the OMO had been completed by others. '

                users[message.chat.id]['state'] = 'affidavit4.2.1'

                await message.reply(
                    text='I am entitled to a service charge of $',
                    reply_markup=ReplyKeyboardRemove()
                    )

            case '2':
                users[message.chat.id]['AFFIDAVIT_TEXT'] += 'I found a contractor: '

                users[message.chat.id]['state'] = 'affidavit4.2.2'

                await message.reply(
                    text='Contractor Company Name and worker at site:',
                    reply_markup=ReplyKeyboardRemove()
                    )

            case '3':
                users[message.chat.id]['AFFIDAVIT_TEXT'] += 'I found that the work described in the OMO was partially performed by others. '

                users[message.chat.id]['state'] = 'affidavit4.2.3'

                await message.reply(
                    text='I performed the remaining work described in the OMO and am entitled to a charge in the amount of $',
                    reply_markup=ReplyKeyboardRemove()
                    )

            case _:
                await message.reply(
                    text='You must choose one of the three options.'
                    )

    elif state == 'affidavit4.2.1':
        users[message.chat.id]['AFFIDAVIT_TEXT'] += f'I am entitled to a service charge of $<code>{message.text}</code>'
        await message.reply(
            text='<b>Send video/photo BEFORE:</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'send_media'

    elif state == 'affidavit4.2.2':
        users[message.chat.id]['AFFIDAVIT_TEXT'] += f'<code>{message.text}</code> at the site performing the same repairs I was directed to perform pursuant to OMO #<code>{users[message.chat.id]["OMO"]}</code>. '
        await message.reply(
            text='I am entitled to a service charge of $',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'affidavit4.3.1'

    elif state == 'affidavit4.2.3':
        users[message.chat.id]['AFFIDAVIT_TEXT'] += f'I performed the remaining work described in the OMO and am entitled to a charge in the amount of $<code>{message.text}</code>. (To be compensated for this work, the Contractor must attach an itemized invoice of work performed.)'
        await message.reply(
            text='<b>Send video/photo BEFORE:</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'send_media'

    elif state == 'affidavit4.3.1':
        users[message.chat.id]['AFFIDAVIT_TEXT'] += f'I am entitled to a service charge of $<code>{message.text}</code>. '
        await message.reply(
            text='<b>The individual gave his/her name as:</b>\n\n<i>Click the button below if the individual refused to give his/her name</i>',
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton('The individual refused to give his/her name')]],
                resize_keyboard=True,
                )
            )
        users[message.chat.id]['state'] = 'affidavit4.3.2'

    elif state == 'affidavit4.3.2':
        users[message.chat.id]['AFFIDAVIT_TEXT'] += message.text if message.text == '<code>The individual refused to give his/her name</code>' else f'The individual gave his/her name as: <code>{message.text}</code>'
        await message.reply(
            text='<b>Description of individual (e.g., male, female, tall/short, dark/light hair):</b>',
            reply_markup=ReplyKeyboardRemove()
            )
        users[message.chat.id]['state'] = 'description2'



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

    if state == 'send_media':
        media_group = []
        for msg in media_messages:
            if msg.photo:
                media_group.append(InputMediaPhoto(msg.photo.file_id))

            elif msg.video:
                media_group.append(InputMediaVideo(msg.video.file_id))

        users[message.chat.id]['media_group'] = media_group
        await message.reply(
            text='<b>Send video/photo AFTER:</b>'
            )
        users[message.chat.id]['state'] = 'send_media2'

    if state != 'send_media2':
        return

    for msg in media_messages:
        if msg.photo:
            users[message.chat.id]['media_group'].append(InputMediaPhoto(msg.photo.file_id))

        elif msg.video:
            users[message.chat.id]['media_group'].append(InputMediaVideo(msg.video.file_id))


    users[message.chat.id]['media_group'][-1].caption = f'''OMO: <code>{users[message.chat.id]["OMO"]}</code>
AFFIDAVIT: <code>{users[message.chat.id]["AFFIDAVIT"]}</code>
{users[message.chat.id]["AFFIDAVIT_TEXT"]}
'''


    await bot.send_media_group(
        chat_id=channel_id,
        media=users[message.chat.id]['media_group']
        )

    await message.reply(
        text='Sent to channel',
        reply_markup=ReplyKeyboardRemove()
        )

    await start_message(_, message)

@bot.on_message((filters.photo | filters.video) & filters.private & filters.incoming)
async def media_handler(_, message):
    if message.chat.id not in users:
        await start_message(_, message)
        return

    state = users[message.chat.id]['state']

    if state == 'send_media':
        if message.photo:
            users[message.chat.id]['media_group'] = [InputMediaPhoto(message.photo.file_id)]

        elif message.video:
            users[message.chat.id]['media_group'] = [InputMediaVideo(message.video.file_id)]

        await message.reply(
            text='<b>Send video/photo AFTER:</b>'
            )
        users[message.chat.id]['state'] = 'send_media2'

    if state != 'send_media2':
        return

    if message.photo:
        users[message.chat.id]['media_group'].append(InputMediaPhoto(message.photo.file_id))

    elif message.video:
        users[message.chat.id]['media_group'].append(InputMediaVideo(message.video.file_id))

    caption = f'''OMO: <code>{users[message.chat.id]["OMO"]}</code>
AFFIDAVIT: <code>{users[message.chat.id]["AFFIDAVIT"]}</code>
{users[message.chat.id]["AFFIDAVIT_TEXT"]}
'''
    users[message.chat.id]['media_group'][-1].caption = caption
    await bot.send_media_group(
        chat_id=channel_id,
        media=users[message.chat.id]['media_group']
        )

    await message.reply(
        text='Sent to channel',
        reply_markup=ReplyKeyboardRemove()
        )

    await start_message(_, message)


bot.run()

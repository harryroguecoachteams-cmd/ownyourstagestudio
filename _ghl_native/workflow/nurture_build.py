"""Writes the nurture emails (nurture_*.html) and nurture.json for the GHL workflow
"RCT - Nurture - pop-up and assessment leads". Same look as the confirm_*.html emails.
Copy comes from Annette's own material: the 3-Minute Speech, the Business Concept
Overview, her August emails, and the live About / Experience / Panelists pages.
Run: python _ghl_native/workflow/nurture_build.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
SITE = 'https://ownyourstagestudio.com'

P = '<p style="margin:0 0 16px;font:16px/1.6 Georgia,serif">%s</p>'
LINK = '<a href="%s" style="color:#B91C1C;text-decoration:underline">%s</a>'
BTN = ('<p style="margin:10px 0 22px"><a href="%s" style="display:inline-block;background:#B91C1C;color:#fff;'
       'text-decoration:none;font:700 15px Arial,sans-serif;padding:14px 26px;border-radius:2px">%s</a></p>')
BTN2 = ('<p style="margin:10px 0 22px"><a href="%s" style="display:inline-block;border:2px solid #B91C1C;color:#B91C1C;'
        'text-decoration:none;font:700 15px Arial,sans-serif;padding:12px 24px;border-radius:2px">%s</a></p>')

HEAD = ('<div style="max-width:600px;margin:0 auto;font-family:Georgia,serif;color:#2E2E2E">\n'
        '<p style="margin:0 0 6px;font:700 13px/1.4 Arial,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#2E2E2E">Own Your Stage Studio</p>\n'
        '<p style="margin:0 0 26px;width:36px;height:3px;background:#B91C1C;font-size:0;line-height:0">&nbsp;</p>')
SIGN = ('<p style="margin:26px 0 0;font:16px/1.6 Georgia,serif">Now Go Steal The Show,<br>Annette</p>\n'
        '<p style="margin:18px 0 0;font:13px/1.6 Arial,sans-serif;color:#5B5552">Annette Knecht Seier | Own Your Stage Studio<br>'
        'The Spotlight Architect<br>' + LINK % (SITE + '/home', 'ownyourstagestudio.com') + '</p>\n'
        '<p style="margin:10px 0 0;font:italic 14px/1.6 Georgia,serif;color:#B91C1C">We build your stage. You steal the show.</p>\n'
        '<p style="margin:30px 0 0;font:12px/1.5 Arial,sans-serif;color:#5B5552">You are receiving this because you asked for the '
        'Readiness Assessment at ownyourstagestudio.com.<br>Own Your Stage Studio, LLC, Florida.</p>\n'
        '</div>\n')

CALL = SITE + '/strategy-session'
ASSESS = SITE + '/assessment'

EMAILS = [
    {
        'file': 'nurture_1a_assessment_reminder.html',
        'action': 'Email 1 (pop-up only): assessment reminder',
        'subject': 'Later has a way of becoming never',
        'preheader': 'The Readiness Assessment link, one more time. About five minutes.',
        'body': [
            P % 'Yesterday you asked for the link to the Readiness Assessment. If you have taken it already, thank you. If it is still waiting in your inbox, consider this your nudge.',
            P % 'I know the pattern well, because it was mine for a very long time. Save it for later. Do it when things calm down. Wait until you feel ready.',
            P % 'Later does not stay later. It becomes never.',
            P % 'The assessment is twelve questions across six pillars: Positioning, Visibility, Credibility, Platform Ownership, Content Leverage and Authority Conversion. It takes about five minutes. There are no good or bad scores, only an honest picture of how visible your authority is today and where to start.',
            BTN % (ASSESS, 'Take the Readiness Assessment'),
            P % 'Over the next two weeks I will send you four more short notes about being seen for the expertise you already have. If that is not for you, the unsubscribe link is at the bottom of every email.',
        ],
    },
    {
        'file': 'nurture_1b_your_result.html',
        'action': 'Email 1 (took the assessment): your result',
        'subject': 'What your result is really telling you',
        'preheader': 'It is not a grade. It is a map.',
        'body': [
            P % 'Hi {{contact.first_name}},',
            P % 'Yesterday you took the Own Your Stage Readiness Assessment, and your result came out as {{contact.assessment_level}}.',
            P % 'That is not a grade. It is a map. Your six pillars show where your authority is already working for you, and where it is being held back.',
            P % 'Your result also named where to start: {{contact.assessment_start_here}}. If you do one thing this week, start there.',
            P % 'Being good at what you do was never the problem. In most fields the most visible voice is not the most qualified one, and the gap between the two is rarely about expertise. It is about who gets seen.',
            P % 'If you would like to go through your result together, pillar by pillar, the Stop Hiding Strategy Call is thirty minutes on Zoom, and it is complimentary. We will name the stage that fits you next, or tell you honestly if none of them fit yet.',
            BTN % (CALL, 'Book a Stop Hiding Strategy Call'),
            P % 'Over the next two weeks I will send you four more short notes. If that is not for you, the unsubscribe link is at the bottom of every email.',
        ],
    },
    {
        'file': 'nurture_2_getting_ready.html',
        'action': 'Email 2: my story',
        'subject': 'I was getting ready to get ready',
        'preheader': 'For a very long time, that was me. Maybe it is you, too.',
        'body': [
            P % 'For a very long time, I was getting ready to get ready to get ready.',
            P % 'One more framework. One more revision. One more improvement. Maybe next month.',
            P % 'I was not hiding from the work. I showed up for my clients, solved problems and delivered results. What I was hiding from was being seen.',
            P % "Getting ready looks productive, sounds responsible and feels safer than being seen. But let's call it what it really is: hiding.",
            P % 'I kept preparing and waiting to feel ready, and that day never came. Then I finally realized I had to step forward before I felt ready.',
            P % 'For years I worked as The Life Reset Coach through Transformation Unlimited, helping ambitious professionals break free from overwhelm. Along the way I kept meeting brilliant coaches, consultants and business owners who had all the expertise in the world and still were not being seen. That is why I created Own Your Stage Studio.',
            P % 'So if any of this sounds familiar, here is what I want you to know. You do not need more expertise. You need visible authority.',
            BTN2 % (SITE + '/about-us', 'Read my story'),
        ],
    },
    {
        'file': 'nurture_3_your_own_stage.html',
        'action': 'Email 3: create your own stage',
        'subject': "Stop waiting to be invited onto someone else's stage",
        'preheader': 'Why we build panels, and what one evening leaves behind.',
        'body': [
            P % "Most experts wait to be invited. A podcast, a summit, a conference slot. Someone else's stage, someone else's audience, someone else's timing.",
            P % 'There is another way. Create your own.',
            P % 'That is what a virtual panel does. You host a conversation on the subject you want to be known for, and up to five other experts join you on a produced stage. Every one of them invites their own audience, so the room is not limited to the people who already know you.',
            P % 'At Own Your Stage Studio, we handle the strategy, the panel, the branding and the production. You lead the conversation.',
            P % 'And it does not end when the room closes. The recording becomes a full replay, highlight videos and short clips for the platforms you already use, so one evening keeps working for months.',
            P % 'Credibility and authority are not prerequisites for taking the stage. They are the result of taking the stage.',
            BTN2 % (SITE + '/experience', 'See how a panel works'),
        ],
    },
    {
        'file': 'nurture_4_three_shifts.html',
        'action': 'Email 4: three shifts, two ways onto the stage',
        'subject': 'Three shifts that make your authority visible',
        'preheader': 'Decide what you want to be known for. Then build the stage.',
        'body': [
            P % 'When I speak at events, I talk about three shifts. They are exactly what we build at Own Your Stage Studio.',
            P % '<b>First, decide what you want to be known for.</b> One clear idea, problem or transformation that people associate with your name.',
            P % "<b>Second, stop waiting to be invited onto someone else's stage.</b> Create your own.",
            P % '<b>Third, make your visibility last.</b> One powerful conversation can create content, relationships and opportunities for months.',
            P % 'Bring those three together, and you have your own authority platform.',
            P % ('There are two ways onto one of our stages. If you are ready to lead the conversation, you host your own panel: '
                 + LINK % (SITE + '/experience', 'the Own Your Stage Experience') + '. If you would rather start smaller, you '
                 + LINK % (SITE + '/panelists', 'join a produced panel as a featured panelist') + ', with a ten minute segment of your own, '
                 'in front of the combined audience, and professional footage of yourself to keep.'),
            P % 'Not sure which fits? That is exactly what the Stop Hiding Strategy Call is for.',
            BTN % (CALL, 'Book a Stop Hiding Strategy Call'),
        ],
    },
    {
        'file': 'nurture_5_strategy_call.html',
        'action': 'Email 5: invitation to the Strategy Call',
        'subject': 'Stop getting ready. Start getting recognized.',
        'preheader': 'Thirty minutes on Zoom, complimentary. Bring the subject you want to be known for.',
        'body': [
            P % 'This is the last note in this short series, so let me be direct.',
            P % 'Every day you stay hidden, someone else becomes known for the work you should be leading.',
            P % 'The Stop Hiding Strategy Call is thirty minutes on Zoom with me, and it is complimentary. We look at where your authority stands today, what you want to be known for, and which stage fits you this year. If none of them fit yet, I will tell you so.',
            P % 'Come with the subject you want to be known for, a rough sense of who you could invite onto your panel, and any date you are working toward.',
            BTN % (CALL, 'Book a Stop Hiding Strategy Call'),
            P % 'Make this the moment you stop getting ready to get ready.',
        ],
    },
]


def main():
    meta = []
    for e in EMAILS:
        html = HEAD + '\n' + '\n'.join(e['body']) + '\n' + SIGN
        (HERE / e['file']).write_text(html, encoding='utf8', newline='\n')
        meta.append({k: e[k] for k in ('file', 'action', 'subject', 'preheader')})
    (HERE / 'nurture.json').write_text(json.dumps(meta, indent=1) + '\n', encoding='utf8', newline='\n')


if __name__ == '__main__':
    main()

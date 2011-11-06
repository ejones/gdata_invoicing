
import sys
import dateutil.parser
import datetime
from getpass import getpass
import getopt
from itertools import *
import json
import operator as op
from itertools import imap

import gdata.service
import gdata.calendar
import gdata.calendar.service

import reportlab
import reportlab.platypus as P
import reportlab.lib.styles as S
import reportlab.lib.colors as C
import reportlab.lib.units as U
'''
import reportlab.pdfbase.pdfmetrics
import reportlab.pdfbase.ttfonts

reportlab.rl_config.warnOnMissingFontGlyphs = 0
reportlab.pdfbase.pdfmetrics.registerFont(
    reportlab.pdfbase.ttfonts.TTFont(
        'Helvetica Light', '/System/Library/Fonts/HelveticaLight.ttf'))
'''

def hexcolor( r0, r1, g0, g1 = None, b0 = None, b1 = None ):
    if g1 is None: b0 = b1 = g0; g0 = g1 = r1; r1 = r0
    return C.Color( ((r0 << 4) + r1) / 256.0,
                    ((g0 << 4) + g1) / 256.0,
                    ((b0 << 4) + b1) / 256.0 )

class obj (object):
    def __init__( self, **kwargs ):
        for k, v in kwargs.iteritems(): setattr( self, k, v )

class CalendarService (gdata.calendar.service.CalendarService):

    def GetEventFeed( self, cal_name = None,
                      start_min = None, start_max = None ):

        cals = self.GetOwnCalendarsFeed()

        cal_link = next( cal.link[ 0 ].href for cal in cals.entry \
                         if not cal_name or cal.title.text == cal_name )

        query = gdata.service.Query( cal_link )
        if start_min: query[ 'start-min' ] = start_min
        if start_max: query[ 'start-max' ] = start_max

        return self.Query(
            query.ToUri(),
            converter = gdata.calendar.CalendarEventFeedFromString )

class Invoice (object):

    def pdf( self ):

      light = hexcolor( 8, 8, 8 )
      dark = hexcolor( 0, 0, 0 )

      ss = S.getSampleStyleSheet()
      tits = ss["title"]
      tits.textColor = dark
      tits.alignment = 0
      tits.spaceAfter += 0.25 * U.inch

      detail = [
          (P.Paragraph('''
           <font name='Helvetica-Bold'>{name}</font><br />{addr}'''.format(
               name = self.invoicer.name,
               addr = self.invoicer.address.replace('\n', '<br />')),
                       ss["BodyText"]),
           'No.:', self.number),
          (None, 'Bill To:',
           P.Paragraph('''
           <font name='Helvetica-Bold'>{name}</font><br />{addr}'''.format(
               name = self.invoicee.name,
               addr = self.invoicee.address.replace('\n', '<br />')),
                       ss["BodyText"])),
          (None, 'Attn:', self.attention),
          (None, 'Period:', self.period),
          (None, 'Date:', self.date),
          (None, 'To be paid within 30 days of invoice date', None),
          (None, 'GST No.:', self.gstNumber),
          (None, 'Bus. No.:', self.businessNumber)]
          
      ds = [('SPAN', (0,0), (0,-1)),
            ('SPAN', (1,5), (-1,5)),
            ('FONT', (1,0), (1, -1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, dark),
            ('VALIGN', (0,0), (-1,-1), 'TOP')]

      subject = P.Paragraph(
          '''<font name='Helvetica-Bold'>Subject:</font>
          {0}'''.format( self.subject ), ss["BodyText"])


      data = sorted (self.feed, key = op.itemgetter (0))


      summary = []
      htotal = sum (imap (op.itemgetter (1), data))
      subtotal = htotal * self.rate
      tax = subtotal * self.gstRate
      total = subtotal + tax
      summary.extend ((('Hours :', '%.2f' % htotal),
                       ('Rate :', '$%.2f/hr' % self.rate),
                       ('Sub-Total :', '$%.2f' % subtotal),
                       ('HST (%.1f%%):' % (self.gstRate * 100),
                        '$%.2f' % tax),
                       ('Total :', '$%.2f' % total)))

      summstyle = [('INNERGRID', (0,0), (-1,-1), 1, light),
                   ('BOX', (0,0), (-1,-1), 1, dark),
                   ('TEXTCOLOR', (0,0), (-1,-1), dark),
                   ('FONT', (0,0), (0, -1), 'Helvetica-Bold'),
                   ('ALIGN', (0,0), (-1,-1), 'RIGHT')]
      
      tdata = list (chain (
          [('Date', 'Hours')], 
          ((date.strftime("%b %d"), '%.2f' % dur) \
                    for date, dur in data)))
      ts = [('INNERGRID', (0,0), (-1,-1), 1, light),
            ('BOX', (0,0), (-1,-1), 1, dark),
            ('LINEBELOW', (0,0), (-1,0), 1, dark),
            ('TEXTCOLOR', (0,0), (-1,-1), dark),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT')]

      doc = P.SimpleDocTemplate( self.filename )
      doc.build([
          P.Paragraph( self.title, tits ),
          P.Table( detail, style = ds, hAlign = 'LEFT',
                   colWidths = (doc.width /2.0, doc.width /8.0,
                                doc.width * 3.0 / 8.0) ),
          P.Spacer( doc.width, 0.5 * U.inch ),
          subject,
          P.Spacer( doc.width, 0.25 * U.inch ),
          P.Table( tdata, style = ts, hAlign = 'LEFT',
                   colWidths = (doc.width / 2.0, doc.width / 2.0) ),
          P.Table( summary, style = summstyle, hAlign = 'LEFT',
                   colWidths = (doc.width / 2.0, doc.width / 2.0) ) ])

def main(filename = '', user = '', password = '', range_min = '',
         range_max = '', calendar = '', **invoice_attrs):

    def usage( code = 2 ):
        print ('''
usage: python '''+sys.argv[0]+''' filename [options]
Creates a PDF invoice at filename from appointments on a Google Calendar.

More information: 'python '''+sys.argv[0]+''' -h'
Configuration:
-j, --json JSON-expr    : a JSON object containing extra configuration
-f, --file filename     : name of the generated PDF file. can also be provided
                        :   by configuration or through the JSON snippet
                        :   (see below). If none of the above qualify, the
                        :   default filename is 'tmp.pdf'.
-h, --help              : more information

The JSON can any subset of the following parameters:
{
   "user": "string",
   "password": "string",
   "range": {
     "min": "string",
     "max": "string" },
   "calendar": "string",

   "invoice": {
       "title": "string",
       "invoicer": {
          "name": "string",
          "address": "string" },
       "invoicee": {
          "name": "string",
          "address": "string" },
       "attention": "string",
       "number": "string",
       "period": "string",
       "date": "string",
       "gstNumber": "string",
       "businessNumber": "string",
       "rate": "number",
       "gstRate": "number",
       "subject": "string" } }

If a password is not available, either from the command-line or configuration
beforehand, it will be prompted from the TTY.
'''         )
        sys.exit( code )

    try: opts, _args = \
         getopt.getopt (sys.argv[1:], "hf:j:", [ "help", "file=", "json=" ])
    except getopt.error, msg: usage()
        
    optd = dict (opts)
    if optd.get ('-h') or optd.get ('--help'): usage(0)
    config = json.loads (optd.get ('-j') or
                               optd.get ('--json', '{}'))
    filename = config.get ('filename', filename) or 'tmp.pdf'
    user = config.get ('user', user)
    password = config.get ('password', password) or getpass()
    range_min = (config.get ('range') or {}).get ('min', range_min)
    range_max = (config.get ('range') or {}).get ('max', range_max)
    calendar = config.get ('calendar', calendar)

    srv = CalendarService(); srv.email = user; srv.password = password
    srv.ProgrammaticLogin()
    feed = srv.GetEventFeed( calendar, range_min, range_max )

    def rows():
        for ev in feed.entry:
            time = ev.when[0]
            start = dateutil.parser.parse( time.start_time )
            end = dateutil.parser.parse( time.end_time )
            yield (start, (end - start).seconds / 3600.0)

    invoice = Invoice()
    invoice.feed = rows(); invoice.filename = filename
    for k, v in config.get('invoice', invoice_attrs).iteritems():
        if k in ('invoicer', 'invoicee'):
            v = obj (**v)
        setattr (invoice, k, v)
    invoice.pdf()

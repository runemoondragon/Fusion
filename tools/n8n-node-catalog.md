## ActionNetwork
**Description**: Consume the Action Network API
**Credentials**: {
          name: actionNetworkApi, required: true
        }
**Actions**:
- Action Network

## ActiveCampaign
**Description**: Create and edit data in ActiveCampaign
**Credentials**: {
          name: activeCampaignApi, required: true
        }
**Actions**:
- ActiveCampaign

## ActiveCampaign
**Description**: Handle ActiveCampaign events via webhooks
**Credentials**: {
          name: activeCampaignApi, required: true
        }
**Actions**:
- ActiveCampaign Trigger
- Event Names or IDs

## AcuityScheduling
**Description**: Handle Acuity Scheduling events via webhooks
**Credentials**: {
          name: acuitySchedulingApi, required: true, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:
- Acuity Scheduling Trigger
- Resolve Data

## Adalo
**Description**: Consume Adalo API
**Credentials**: {
          name: adaloApi, required: true
        }
**Actions**:
- Collection ID

## Affinity
**Description**: Consume Affinity API
**Credentials**: {
          name: affinityApi, required: true
        }
**Actions**:


## Affinity
**Description**: Handle Affinity events via webhooks
**Credentials**: {
          name: affinityApi, required: true
        }
**Actions**:
- Affinity Trigger

## AgileCrm
**Description**: Consume Agile CRM API
**Credentials**: {
          name: agileCrmApi, required: true
        }
**Actions**:
- Agile CRM

## AiTransform
**Description**: Modify data based on instructions written in plain english
**Credentials**: None
**Actions**:
- AI Transform
- Code Generated For Prompt
- Generated JavaScript

## Airtable
**Description**: Read, update, write and delete data from Airtable
**Credentials**: None
**Actions**:


## Airtable
**Description**: Starts the workflow when Airtable events occur
**Credentials**: {
          name: airtableApi, required: true, displayOptions: {
            show: {
              authentication: [airtableApi
**Actions**:
- Airtable Trigger
- By URL
- ID
- Trigger Field
- Download Attachments
- Download Fields
- Additional Fields
- View ID

## v1
**Description**: Read, update, write and delete data from Airtable
**Credentials**: {
      name: airtableApi, required: true, displayOptions: {
        show: {
          authentication: [airtableApi
**Actions**:
- This type of connection (API Key) was deprecated and can
- By URL
- ID
- Add All Fields
- Return All
- Download Attachments
- Download Fields
- Additional Options
- Filter By Formula
- Update All Fields
- Bulk Size
- Ignore Fields

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## Airtop
**Description**: Scrape and control any site with Airtop
**Credentials**: {
          name: airtopApi, required: true
        }
**Actions**:


## Amqp
**Description**: Sends a raw-message via AMQP 1.0, executed once per item
**Credentials**: {
          name: amqp, required: true, testedBy: amqpConnectionTest
        }
**Actions**:
- AMQP Sender
- Queue / Topic
- Container ID
- Data as Object
- Reconnect Limit
- Send Property

## Amqp
**Description**: Listens to AMQP 1.0 Messages
**Credentials**: {
          name: amqp, required: true
        }
**Actions**:
- AMQP Trigger
- Queue / Topic
- Container ID
- Convert Body To String
- JSON Parse Body
- Messages per Cicle
- Only Body
- Parallel Processing
- Reconnect Limit
- Sleep Time

## ApiTemplateIo
**Description**: Consume the APITemplate.io API
**Credentials**: {
          name: apiTemplateIoApi, required: true
        }
**Actions**:
- APITemplate.io
- Template Name or ID
- JSON Parameters
- Put Output File in Field
- Overrides (JSON)
- Properties (JSON)
- File Name

## Asana
**Description**: Consume Asana REST API
**Credentials**: {
          name: asanaApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- Parent Task ID
- Additional Fields
- Assignee Name or ID
- Assignee Status
- Due On
- Workspace Name or ID
- Return All
- Field Names or IDs
- Task ID
- Project Name or ID
- Section Name or ID
- Completed Since
- Modified Since
- Project Names or IDs
- Is Text HTML
- HTML Text
- Comment ID
- Insert After
- Insert Before
- Tags Name or ID
- User ID
- Team Name or ID
- Privacy Setting
- Project ID
- Teams Name or ID
- Update Fields

## Asana
**Description**: Starts the workflow when Asana events occur.
**Credentials**: {
          name: asanaApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- Asana Trigger
- Workspace Name or ID

## Automizy
**Description**: Consume Automizy API
**Credentials**: {
          name: automizyApi, required: true
        }
**Actions**:
- This service may no longer exist and will be removed from n8n in a future release.

## Autopilot
**Description**: Consume Autopilot API
**Credentials**: {
          name: autopilotApi, required: true
        }
**Actions**:


## Autopilot
**Description**: Handle Autopilot events via webhooks
**Credentials**: {
          name: autopilotApi, required: true
        }
**Actions**:
- Autopilot Trigger

## Aws
**Description**: Invoke functions on AWS Lambda
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS Lambda
- Function Name or ID
- Invocation Type
- JSON Input

## Aws
**Description**: Sends data to AWS SNS
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS SNS
- Display Name
- Fifo Topic
- From List
- By URL
- ID

## Aws
**Description**: Handle AWS SNS events via webhooks
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS SNS Trigger
- From List
- By URL
- ID

## CertificateManager
**Description**: Sends data to AWS Certificate Manager
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS Certificate Manager

## Comprehend
**Description**: Sends data to Amazon Comprehend
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS Comprehend
- Language Code
- Additional Fields
- Endpoint Arn

## DynamoDB
**Description**: Consume the AWS DynamoDB API
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS DynamoDB

## ELB
**Description**: Sends data to AWS ELB API
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS ELB

## Rekognition
**Description**: Sends data to AWS Rekognition
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS Rekognition
- Binary File
- Input Binary Field
- Additional Fields
- Regions of Interest
- Region of Interest
- Word Filter
- Min Bounding Box Height
- Min Bounding Box Width
- Min Confidence
- Max Labels

## S3
**Description**: Sends data to AWS S3
**Credentials**: None
**Actions**:
- AwsS3

## V1
**Description**: Sends data to AWS S3
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS S3

## V2
**Description**: Sends data to AWS S3
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS S3

## SES
**Description**: Sends data to AWS SES
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS SES
- From Email
- Template Name
- Template Content
- Template Subject
- Success Redirection URL
- Failure Redirection URL
- Additional Fields
- Configuration Set Name
- Update Fields
- Return All
- Is Body HTML
- To Addresses
- Template Name or ID
- Template Data
- Bcc Addresses
- Cc Addresses
- Reply To Addresses
- Return Path
- Return Path ARN
- Source ARN
- Subject Part
- Html Part
- Text Part

## SQS
**Description**: Sends messages to AWS SQS
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS SQS
- Queue Name or ID
- Queue Type
- Send Input Data
- Message Group ID
- Delay Seconds
- Message Attributes
- Property Name
- Message Deduplication ID

## Textract
**Description**: Sends data to Amazon Textract
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS Textract
- Input Data Field Name

## Transcribe
**Description**: Sends data to AWS Transcribe
**Credentials**: {
          name: aws, required: true
        }
**Actions**:
- AWS Transcribe
- Job Name
- Media File URI
- Detect Language
- Channel Identification
- Max Alternatives
- Max Speaker Labels
- Vocabulary Name
- Vocabulary Filter Name
- Vocabulary Filter Method
- Return Transcript
- Return All
- Job Name Contains

## BambooHr
**Description**: No description
**Credentials**: None
**Actions**:


## Bannerbear
**Description**: Consume Bannerbear API
**Credentials**: {
          name: bannerbearApi, required: true
        }
**Actions**:


## Baserow
**Description**: Consume the Baserow API
**Credentials**: {
          name: baserowApi, required: true
        }
**Actions**:


## Beeminder
**Description**: Consume Beeminder API
**Credentials**: {
          name: beeminderApi, required: true
        }
**Actions**:
- Goal Name or ID
- Return All
- Datapoint ID
- Additional Fields
- Request ID
- Update Fields

## Bitbucket
**Description**: Handle Bitbucket events via webhooks
**Credentials**: {
          name: bitbucketApi, required: true, testedBy: bitbucketApiTest
        }
**Actions**:
- Bitbucket Trigger
- Workspace Name or ID
- Event Names or IDs
- Repository Name or ID

## Bitly
**Description**: Consume Bitly API
**Credentials**: {
          name: bitlyApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:


## Bitwarden
**Description**: Consume the Bitwarden API
**Credentials**: {
          name: bitwardenApi, required: true
        }
**Actions**:


## Box
**Description**: Consume Box API
**Credentials**: {
          name: boxOAuth2Api, required: true
        }
**Actions**:


## Box
**Description**: Starts the workflow when Box events occur
**Credentials**: {
          name: boxOAuth2Api, required: true
        }
**Actions**:
- Box Trigger
- Target Type
- Target ID

## Brandfetch
**Description**: Consume Brandfetch API
**Credentials**: {
          name: brandfetchApi, required: true
        }
**Actions**:
- Image Type
- Image Format

## Brevo
**Description**: Consume Brevo API
**Credentials**: {
          name: sendInBlueApi, required: true
        }
**Actions**:


## Brevo
**Description**: Starts the workflow when Brevo events occur
**Credentials**: {
          name: sendInBlueApi, required: true, displayOptions: {
            show: {}
          }
        }
**Actions**:
- Brevo Trigger
- Trigger On

## Bubble
**Description**: Consume the Bubble Data API
**Credentials**: {
          name: bubbleApi, required: true
        }
**Actions**:


## Cal
**Description**: Handle Cal.com events via webhooks
**Credentials**: {
          name: calApi, required: true
        }
**Actions**:
- Cal.com Trigger
- API Version
- App ID
- EventType Name or ID
- Payload Template

## Calendly
**Description**: Starts the workflow when Calendly events occur
**Credentials**: {
          name: calendlyApi, required: true, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:
- Calendly Trigger

## Chargebee
**Description**: Retrieve data from Chargebee API
**Credentials**: {
          name: chargebeeApi, required: true
        }
**Actions**:
- User ID
- First Name
- Last Name
- Custom Properties
- Property Name
- Property Value
- Max Results
- Invoice Date
- Invoice Amount
- Invoice ID
- Subscription ID
- Schedule End of Term

## Chargebee
**Description**: Starts the workflow when Chargebee events occur
**Credentials**: None
**Actions**:
- Chargebee Trigger

## CircleCi
**Description**: Consume CircleCI API
**Credentials**: {
          name: circleCiApi, required: true
        }
**Actions**:
- CircleCI

## Webex
**Description**: Consume the Cisco Webex API
**Credentials**: {
          name: ciscoWebexOAuth2Api, required: true
        }
**Actions**:
- Webex by Cisco

## Webex
**Description**: Starts the workflow when Cisco Webex events occur.
**Credentials**: {
          name: ciscoWebexOAuth2Api, required: true
        }
**Actions**:
- Webex by Cisco Trigger
- Resolve Data
- Has Files
- Is Locked
- Is Moderator
- Mentioned People
- Message ID
- Owned By
- Person Email
- Person ID
- Room ID
- Room Type
- Call Type

## Clearbit
**Description**: Consume Clearbit API
**Credentials**: {
          name: clearbitApi, required: true
        }
**Actions**:


## ClickUp
**Description**: Consume ClickUp API (Beta)
**Credentials**: {
          name: clickUpApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- ClickUp

## ClickUp
**Description**: Handle ClickUp events via webhooks (Beta)
**Credentials**: {
          name: clickUpApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- ClickUp Trigger
- Team Name or ID
- Folder ID
- List ID
- Space ID
- Task ID

## Clockify
**Description**: Consume Clockify REST API
**Credentials**: {
          name: clockifyApi, required: true
        }
**Actions**:
- Workspace Name or ID

## Clockify
**Description**: Listens to Clockify events
**Credentials**: {
          name: clockifyApi, required: true
        }
**Actions**:
- Clockify Trigger
- Workspace Name or ID

## Cloudflare
**Description**: Consume Cloudflare API
**Credentials**: {
          name: cloudflareApi, required: true
        }
**Actions**:


## Cockpit
**Description**: Consume Cockpit API
**Credentials**: {
          name: cockpitApi, required: true
        }
**Actions**:


## Coda
**Description**: Consume Coda API
**Credentials**: {
          name: codaApi, required: true
        }
**Actions**:


## Code
**Description**: Run custom JavaScript or Python code
**Credentials**: None
**Actions**:


## CoinGecko
**Description**: Consume CoinGecko API
**Credentials**: None
**Actions**:
- CoinGecko

## CompareDatasets
**Description**: Compare two inputs for changes
**Credentials**: None
**Actions**:
- Compare Datasets
- Items from different branches are paired together when the fields below match. If paired, the rest of the fields are compared to determine whether the items are the same or different
- Fields to Match
- Input A Field
- Input B Field
- When There Are Differences
- Fuzzy Compare
- For Everything Except
- Fields to Skip Comparing
- Disable Dot Notation
- Multiple Matches

## Compression
**Description**: Compress and decompress files
**Credentials**: None
**Actions**:
- Input Binary Field(s)
- Output Format
- File Name
- Put Output File in Field
- Output File Prefix
- Output Prefix

## Contentful
**Description**: Consume Contentful API
**Credentials**: {
          name: contentfulApi, required: true
        }
**Actions**:


## ConvertKit
**Description**: Consume ConvertKit API
**Credentials**: {
          name: convertKitApi, required: true
        }
**Actions**:
- ConvertKit

## ConvertKit
**Description**: Handle ConvertKit events via webhooks
**Credentials**: {
          name: convertKitApi, required: true
        }
**Actions**:
- ConvertKit Trigger
- Form Name or ID
- Sequence Name or ID
- Initiating Link
- Product ID
- Tag Name or ID

## Copper
**Description**: Consume the Copper API
**Credentials**: {
          name: copperApi, required: true
        }
**Actions**:


## Copper
**Description**: Handle Copper events via webhooks
**Credentials**: {
          name: copperApi, required: true
        }
**Actions**:
- Copper Trigger

## Cortex
**Description**: Apply the Cortex analyzer/responder on the given entity
**Credentials**: {
          name: cortexApi, required: true
        }
**Actions**:


## CrateDb
**Description**: Add and update data in CrateDB
**Credentials**: {
          name: crateDb, required: true
        }
**Actions**:
- CrateDB
- Update Key
- Return Fields
- Additional Fields
- Query Parameters

## Cron
**Description**: Triggers the workflow at a specific time
**Credentials**: None
**Actions**:
- This workflow will run on the schedule you define here once you <a data-key=
- Trigger Times

## CrowdDev
**Description**: crowd.dev is an open-source suite of community and data tools built to unlock community-led growth for your organization.
**Credentials**: {
          name: crowdDevApi, required: true
        }
**Actions**:
- crowd.dev

## CrowdDev
**Description**: Starts the workflow when crowd.dev events occur.
**Credentials**: {
          name: crowdDevApi, required: true
        }
**Actions**:
- crowd.dev Trigger

## Crypto
**Description**: Provide cryptographic utilities
**Credentials**: None
**Actions**:
- Binary File
- Binary Property Name
- Property Name
- Algorithm Name or ID
- Private Key

## CustomerIo
**Description**: Consume Customer.io API
**Credentials**: {
          name: customerIoApi, required: true
        }
**Actions**:
- Customer.io

## CustomerIo
**Description**: Starts the workflow on a Customer.io update (Beta)
**Credentials**: {
          name: customerIoApi, required: true
        }
**Actions**:
- Customer.io Trigger

## DateTime
**Description**: Allows you to manipulate date and time values
**Credentials**: None
**Actions**:
- Date & Time

## V1
**Description**: Allows you to manipulate date and time values
**Credentials**: None
**Actions**:
- Date & Time
- More powerful date functionality is available in <a href=
- Property Name
- Custom Format
- To Format
- From Format
- From Timezone Name or ID
- To Timezone Name or ID
- Date Value
- Time Unit

## V2
**Description**: Manipulate date and time values
**Credentials**: None
**Actions**:


## DebugHelper
**Description**: Causes problems intentionally and generates useful data for debugging
**Credentials**: None
**Actions**:
- DebugHelper
- Error Type
- Error Message
- Memory Size to Generate
- Data Type
- NanoId Alphabet
- NanoId Length
- Number of Items to Generate
- Output as Single Array

## DeepL
**Description**: Translate data using DeepL
**Credentials**: {
          name: deepLApi, required: true
        }
**Actions**:
- DeepL

## Demio
**Description**: Consume the Demio API
**Credentials**: {
          name: demioApi, required: true
        }
**Actions**:


## Dhl
**Description**: Consume DHL API
**Credentials**: {
          name: dhlApi, required: true, testedBy: dhlApiCredentialTest
        }
**Actions**:
- DHL
- Tracking Number

## Discord
**Description**: Sends data to Discord
**Credentials**: None
**Actions**:


## v1
**Description**: Sends data to Discord
**Credentials**: None
**Actions**:
- Webhook URL
- Additional Fields
- Allowed Mentions
- Avatar URL
- JSON Payload
- TTS

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## Discourse
**Description**: Consume Discourse API
**Credentials**: {
          name: discourseApi, required: true
        }
**Actions**:


## Disqus
**Description**: Access data on Disqus
**Credentials**: {
          name: disqusApi, required: true
        }
**Actions**:
- Forum Name
- Additional Fields
- Return All

## Drift
**Description**: Consume Drift API
**Credentials**: {
          name: driftApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:


## Dropbox
**Description**: Access data on Dropbox
**Credentials**: {
          name: dropboxApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- From Path
- To Path
- Delete Path
- File Path
- Put Output File in Field
- Binary File
- File Content
- Input Binary Field
- File Status
- Return All
- File Categories
- File Extensions
- Folder Path
- Include Deleted
- Include Shared Members
- Include Mounted Folders
- Include Non Downloadable Files

## Dropcontact
**Description**: Find B2B emails and enrich contacts
**Credentials**: {
          name: dropcontactApi, required: true
        }
**Actions**:
- Request ID
- Simplify Output (Faster)
- Additional Fields
- Company SIREN Number
- Company SIRET Code
- Company Name
- First Name
- Full Name
- Last Name
- LinkedIn Profile
- Phone Number
- Data Fetch Wait Time
- French Company Enrich

## E2eTest
**Description**: Dummy node used for e2e testing
**Credentials**: None
**Actions**:
- E2E Test
- Field ID
- Remote Options Name or ID
- Resource Locator
- From List
- By URL
- ID
- Resource Mapping Component
- Other Non Important Field

## ERPNext
**Description**: Consume ERPNext API
**Credentials**: {
          name: erpNextApi, required: true
        }
**Actions**:
- ERPNext

## EditImage
**Description**: Adds a blur to the image and so makes it less sharp
**Credentials**: None
**Actions**:
- Background Color
- Image Width
- Image Height
- Start Position X
- Start Position Y
- End Position X
- End Position Y
- Corner Radius
- Font Size
- Font Color
- Position X
- Position Y
- Max Line Length
- Border Width
- Border Height
- Border Color
- Composite Image Property
- Degrees X
- Degrees Y
- Edit Image
- Property Name
- Font Name or ID
- File Name

## Egoi
**Description**: Consume E-goi API
**Credentials**: {
          name: egoiApi, required: true
        }
**Actions**:
- E-goi
- List Name or ID
- Contact ID
- Resolve Data
- Additional Fields
- Birth Date
- Extra Fields
- Extra Field
- Field Name or ID
- First Name
- Last Name
- Tag Names or IDs
- Update Fields
- Return All

## ElasticSecurity
**Description**: Consume the Elastic Security API
**Credentials**: {
          name: elasticSecurityApi, required: true
        }
**Actions**:
- Elastic Security

## Elasticsearch
**Description**: Consume the Elasticsearch API
**Credentials**: {
          name: elasticsearchApi, required: true
        }
**Actions**:


## EmailReadImap
**Description**: Triggers the workflow when a new email is received
**Credentials**: None
**Actions**:
- Email Trigger (IMAP)

## v1
**Description**: Triggers the workflow when a new email is received
**Credentials**: {
      name: imap, required: true, testedBy: imapConnectionTest
    }
**Actions**:
- Email Trigger (IMAP)
- Mailbox Name
- Download Attachments
- Property Prefix Name
- Custom Email Rules
- Ignore SSL Issues (Insecure)
- Force Reconnect

## v2
**Description**: Triggers the workflow when a new email is received
**Credentials**: {
      name: imap, required: true, testedBy: imapConnectionTest
    }
**Actions**:
- Email Trigger (IMAP)
- Mailbox Name
- Download Attachments
- Property Prefix Name
- Custom Email Rules
- Force Reconnect Every Minutes

## EmailSend
**Description**: Sends an email using SMTP protocol
**Credentials**: None
**Actions**:
- Send Email

## v1
**Description**: Sends an Email
**Credentials**: {
      name: smtp, required: true
    }
**Actions**:
- Send Email
- From Email
- To Email
- CC Email
- BCC Email
- HTML
- Ignore SSL Issues (Insecure)
- Reply To

## v2
**Description**: Sends an email using SMTP protocol
**Credentials**: {
      name: smtp, required: true, testedBy: smtpConnectionTest
    }
**Actions**:
- Send Email

## Emelia
**Description**: Consume the Emelia API
**Credentials**: {
          name: emeliaApi, required: true, testedBy: emeliaApiTest
        }
**Actions**:


## Emelia
**Description**: Handle Emelia campaign activity events via webhooks
**Credentials**: {
          name: emeliaApi, required: true, testedBy: emeliaApiTest
        }
**Actions**:
- Emelia Trigger
- Campaign Name or ID

## ErrorTrigger
**Description**: Triggers the workflow when another workflow has an error
**Credentials**: None
**Actions**:
- Error Trigger
- This node will trigger when there is an error in another workflow, as long as that workflow is set up to do so. <a href=

## EvaluationMetrics
**Description**: Define the metrics returned for workflow evaluation
**Credentials**: None
**Actions**:
- Evaluation Metrics
- Define the evaluation metrics returned in your report. Only numeric values are supported. <a href=
- Metrics to Return

## Eventbrite
**Description**: Handle Eventbrite events via webhooks
**Credentials**: {
          name: eventbriteApi, required: true, displayOptions: {
            show: {
              authentication: [privateKey
**Actions**:
- Eventbrite Trigger
- Organization Name or ID
- Event Name or ID
- Resolve Data

## ExecuteCommand
**Description**: Executes a command on the host
**Credentials**: None
**Actions**:
- Execute Command
- Execute Once

## ExecuteWorkflow
**Description**: Execute another workflow
**Credentials**: None
**Actions**:
- Execute Sub-workflow
- This node is out of date. Please upgrade by removing it and adding a new one
- Workflow ID
- Workflow Path
- Workflow JSON
- Workflow URL
- Any data you pass into this node will be output by the Execute Workflow Trigger. <a href=
- Workflow Inputs
- Wait For Sub-Workflow Completion

## ExecuteWorkflowTrigger
**Description**: Helpers for calling other n8n workflows. Used for designing modular, microservice-like workflows.
**Credentials**: None
**Actions**:
- Execute Workflow Trigger
- When an \u2018execute workflow\u2019 node calls this workflow, the execution starts here. Any data passed into the 
- This node is out of date. Please upgrade by removing it and adding a new one
- Input data mode
- Provide an example object to infer fields and their types.<br>To allow any type for a given field, set the value to null.
- JSON Example
- Workflow Input Schema

## ExecutionData
**Description**: Add execution data for search
**Credentials**: None
**Actions**:
- Execution Data
- Save important data using this node. It will be displayed on each execution for easy reference and you can filter by it.<br />Filtering is available on Pro and Enterprise plans. <a href=
- Data to Save

## Facebook
**Description**: Interacts with Facebook using the Graph API
**Credentials**: {
          name: facebookGraphApi, required: true
        }
**Actions**:
- Facebook Graph API
- Host URL
- HTTP Request Method
- Graph API Version
- Ignore SSL Issues (Insecure)
- Send Binary File
- Input Binary Field
- Query Parameters
- Query Parameters JSON

## Facebook
**Description**: Starts the workflow when Facebook events occur
**Credentials**: {
          name: facebookGraphAppApi, required: true
        }
**Actions**:
- Facebook Trigger
- APP ID
- To watch Whatsapp business account events use the Whatsapp trigger node
- Field Names or IDs
- Include Values

## FacebookLeadAds
**Description**: Handle Facebook Lead Ads events via webhooks
**Credentials**: {
          name: facebookLeadAdsOAuth2Api, required: true
        }
**Actions**:
- Facebook Lead Ads Trigger
- Due to Facebook API limitations, you can use just one Facebook Lead Ads trigger for each Facebook App
- From List
- By ID
- Simplify Output

## Figma
**Description**: Starts the workflow when Figma events occur
**Credentials**: {
          name: figmaApi, required: true
        }
**Actions**:
- Figma Trigger (Beta)
- Team ID
- Trigger On

## FileMaker
**Description**: Retrieve data from the FileMaker data API
**Credentials**: {
          name: fileMaker, required: true
        }
**Actions**:
- FileMaker
- Layout Name or ID
- Record ID
- Get Portals
- Portals Name or ID
- Response Layout Name or ID
- Field Name or ID
- Sort Data?
- Before Find Script
- Script Name or ID
- Script Parameter
- Before Sort Script
- After Sort Script
- fieldData
- Mod ID

## ConvertToFile
**Description**: Convert JSON data to binary data
**Credentials**: None
**Actions**:
- Convert to File

## ExtractFromFile
**Description**: Convert binary data to JSON
**Credentials**: None
**Actions**:
- Extract from File

## ReadWriteFile
**Description**: Read or write files from the computer that runs n8n
**Credentials**: None
**Actions**:
- Read/Write Files from Disk
- Use this node to read and write files on the same computer running n8n. To handle files between different computers please use other nodes (e.g. FTP, HTTP Request, AWS).

## Filter
**Description**: Remove items matching a condition
**Credentials**: None
**Actions**:


## V1
**Description**: The type of values to compare
**Credentials**: None
**Actions**:
- Value 1
- Value 2
- Date & Time
- Combine Conditions

## V2
**Description**: Whether to ignore letter case when evaluating conditions
**Credentials**: None
**Actions**:
- Ignore Case

## Flow
**Description**: Consume Flow API
**Credentials**: {
          name: flowApi, required: true
        }
**Actions**:


## Flow
**Description**: Handle Flow events via webhooks
**Credentials**: {
          name: flowApi, required: true
        }
**Actions**:
- Flow Trigger
- Project ID
- Task ID

## Form
**Description**: Whether to limit the time this node should wait for a user response before execution resumes
**Credentials**: None
**Actions**:
- Limit Wait Time
- Define Form
- Form Fields
- Button Label
- Custom Form Styling
- On n8n Form Submission
- URL
- Completion Title
- Completion Message
- Input Data Field Name
- Completion Page Title
- n8n Form
- An n8n Form Trigger node must be set up before this node
- Page Type

## Form
**Description**: Generate webforms in n8n and pass their responses to the workflow
**Credentials**: None
**Actions**:
- n8n Form Trigger

## v1
**Description**: Generate webforms in n8n and pass their responses to the workflow
**Credentials**: None
**Actions**:
- n8n Form Trigger
- Form Submitted Text

## v2
**Description**: Whether to use the workflow timezone set in node
**Credentials**: {
      // eslint-disable-next-line n8n-nodes-base/node-class-description-credentials-name-unsuffixed
      name: httpBasicAuth, required: true, displayOptions: {
        show: {
          [import_interfaces.FORM_TRIGGER_AUTHENTICATION_PROPERTY
**Actions**:
- Use Workflow Timezone
- n8n Form Trigger
- In the 
- Build multi-step forms by adding a form page later in your workflow
- Button Label
- Ignore Bots
- Custom Form Styling

## FormIo
**Description**: Handle form.io events via webhooks
**Credentials**: {
          name: formIoApi, required: true
        }
**Actions**:
- Form.io Trigger
- Project Name or ID
- Form Name or ID
- Trigger Events

## Formstack
**Description**: Starts the workflow on a Formstack form submission.
**Credentials**: {
          name: formstackApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- Formstack Trigger
- Form Name or ID

## Freshdesk
**Description**: Consume Freshdesk API
**Credentials**: {
          name: freshdeskApi, required: true
        }
**Actions**:
- Requester Identification
- JSON Parameters
- Agent Name or ID
- CC Emails
- Company Name or ID
- Due By
- Email Config ID
- FR Due By
- Group Name or ID
- Product Name or ID
- Custom Fields
- Custom fields
- Ticket ID
- Update Fields
- Requester Value
- Return All
- Company ID
- Order By
- Requester Email
- Requester ID
- Updated Since

## Freshservice
**Description**: Consume the Freshservice API
**Credentials**: {
          name: freshserviceApi, required: true
        }
**Actions**:


## FreshworksCrm
**Description**: Consume the Freshworks CRM API
**Credentials**: {
          name: freshworksCrmApi, required: true
        }
**Actions**:
- Freshworks CRM

## Ftp
**Description**: Transfer files via FTP or SFTP
**Credentials**: {
          // nodelinter-ignore-next-line
          name: ftp, required: true, displayOptions: {
            show: {
              protocol: [ftp
**Actions**:
- FTP
- Put Output File in Field
- Old Path
- New Path
- Create Directories
- Binary File
- Input Binary Field
- File Content

## Function
**Description**: Run custom function code which gets executed once and allows you to add, remove, change and replace items
**Credentials**: None
**Actions**:
- A newer version of this node type is available, called the \u2018Code\u2019 node
- JavaScript Code

## FunctionItem
**Description**: Run custom function code which gets executed once per item
**Credentials**: None
**Actions**:
- Function Item
- A newer version of this node type is available, called the \u2018Code\u2019 node
- JavaScript Code

## GetResponse
**Description**: Consume GetResponse API
**Credentials**: {
          name: getResponseApi, required: true, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:
- GetResponse

## GetResponse
**Description**: Starts the workflow when GetResponse events occur
**Credentials**: {
          name: getResponseApi, required: true, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:
- GetResponse Trigger
- List Names or IDs
- Delete Current Subscription

## Ghost
**Description**: Consume Ghost API
**Credentials**: {
          name: ghostAdminApi, required: true, displayOptions: {
            show: {
              source: [adminApi
**Actions**:


## Git
**Description**: Control git.
**Credentials**: {
          name: gitPassword, required: true, displayOptions: {
            show: {
              authentication: [gitPassword
**Actions**:
- Repository Path
- New Repository Path

## Github
**Description**: Consume GitHub API
**Credentials**: {
          name: githubApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- GitHub
- Your execution will pause until a webhook is called. This URL will be generated at runtime and passed to your Github workflow as a resumeUrl input.
- Repository Owner
- By Name
- Repository Name
- By File Name
- By ID
- From List
- File Path
- Binary File
- File Content
- Input Binary Field
- Commit Message
- Additional Parameters
- As Binary Property
- Put Output File in Field
- Issue Number
- Edit Fields
- State Reason
- Lock Reason
- Additional Fields
- Target Commitish
- Release ID
- Tag Name
- Return All
- Updated Since
- PR Number
- Review ID
- Commit ID

## Github
**Description**: Starts the workflow when Github events occur
**Credentials**: {
          name: githubApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- Github Trigger
- Only members with owner privileges for an organization or admin privileges for a repository can set up the webhooks this node requires.
- Repository Owner
- By Name
- Repository Name
- Insecure SSL

## Gitlab
**Description**: Retrieve data from GitLab API
**Credentials**: {
          name: gitlabApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- GitLab
- Project Owner
- Project Name
- Due Date
- Issue Number
- Edit Fields
- Lock Reason
- Additional Fields
- Project ID
- Tag Name
- Return All
- Order By
- Released At
- Updated After
- File Path
- Additional Parameters
- As Binary Property
- Put Output File in Field
- Binary File
- File Content
- Input Binary Field
- Commit Message
- Start Branch

## Gitlab
**Description**: Triggered when a new comment is made on commits, merge requests, issues, and code snippets
**Credentials**: {
          name: gitlabApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- GitLab Trigger
- Repository Owner
- Repository Name

## GoToWebinar
**Description**: Consume the GoToWebinar API
**Credentials**: {
          name: goToWebinarOAuth2Api, required: true
        }
**Actions**:
- GoToWebinar

## Gong
**Description**: Interact with Gong API
**Credentials**: {
          name: gongApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:


## Ads
**Description**: Use the Google Ads API
**Credentials**: {
          name: googleAdsOAuth2Api, required: true, testedBy: {
            request: {
              method: GET, url: /v17/customers:listAccessibleCustomers
            }
          }
        }
**Actions**:
- Google Ads
- Divide field names expressed with <i>micros</i> by 1,000,000 to get the actual value

## Analytics
**Description**: Use the Google Analytics API
**Credentials**: None
**Actions**:
- Google Analytics

## v1
**Description**: Use the Google Analytics API
**Credentials**: {
      name: googleAnalyticsOAuth2, required: true
    }
**Actions**:
- Google Analytics

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## BigQuery
**Description**: Consume Google BigQuery API
**Credentials**: None
**Actions**:
- Google BigQuery

## v1
**Description**: Consume Google BigQuery API
**Credentials**: {
      name: googleApi, required: true, displayOptions: {
        show: {
          authentication: [serviceAccount
**Actions**:
- Google BigQuery

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## Books
**Description**: Read data from Google Books
**Credentials**: {
          name: googleApi, required: true, displayOptions: {
            show: {
              authentication: [serviceAccount
**Actions**:
- Google Books
- My Library
- Search Query
- User ID
- Bookshelf ID
- Volume ID
- Volume Position
- Return All

## BusinessProfile
**Description**: Consume Google Business Profile API
**Credentials**: {
          name: googleBusinessProfileOAuth2Api, required: true
        }
**Actions**:
- Google Business Profile

## BusinessProfile
**Description**: Fetches reviews from Google Business Profile and starts the workflow on specified polling intervals.
**Credentials**: {
          name: googleBusinessProfileOAuth2Api, required: true
        }
**Actions**:
- Google Business Profile Trigger
- From list
- By name

## Calendar
**Description**: Consume Google Calendar API
**Credentials**: {
          name: googleCalendarOAuth2Api, required: true
        }
**Actions**:
- Google Calendar
- This node will use the time zone set in n8n\u2019s settings, but you can override this in the workflow settings

## Calendar
**Description**: Starts the workflow when Google Calendar events occur
**Credentials**: {
          name: googleCalendarOAuth2Api, required: true
        }
**Actions**:
- Google Calendar Trigger
- ID
- Trigger On
- Match Term

## Chat
**Description**: Consume Google Chat API
**Credentials**: {
          name: googleApi, required: true, testedBy: testGoogleTokenAuth, displayOptions: {
            show: {
              authentication: [serviceAccount
**Actions**:
- Google Chat

## CloudNaturalLanguage
**Description**: Consume Google Cloud Natural Language API
**Credentials**: {
          name: googleCloudNaturalLanguageOAuth2Api, required: true
        }
**Actions**:
- Google Cloud Natural Language
- Google Cloud Storage URI
- Document Type
- Encoding Type

## CloudStorage
**Description**: Use the Google Cloud Storage API
**Credentials**: {
          name: googleCloudStorageOAuth2Api, required: true, testedBy: {
            request: {
              method: GET, url: /b/
            }
          }
        }
**Actions**:
- Google Cloud Storage

## Contacts
**Description**: Consume Google Contacts API
**Credentials**: {
          name: googleContactsOAuth2Api, required: true
        }
**Actions**:
- Google Contacts

## Docs
**Description**: Consume Google Docs API.
**Credentials**: {
          name: googleApi, required: true, displayOptions: {
            show: {
              authentication: [serviceAccount
**Actions**:
- Google Docs

## Drive
**Description**: Access data on Google Drive
**Credentials**: None
**Actions**:
- Google Drive

## Drive
**Description**: Starts the workflow when Google Drive events occur
**Credentials**: {
          name: googleApi, required: true, displayOptions: {
            show: {
              authentication: [serviceAccount
**Actions**:
- Google Drive Trigger
- Credential Type
- Trigger On
- ID
- Watch For
- Changes within subfolders won
- Drive To Watch
- File Type

## v1
**Description**: Access data on Google Drive
**Credentials**: {
      name: googleApi, required: true, displayOptions: {
        show: {
          authentication: [serviceAccount
**Actions**:
- Google Drive
- ID
- Put Output File in Field
- Google File Conversion
- Google Docs
- Google Drawings
- Google Slides
- Google Sheets
- File Name
- Use Query String
- Query String
- Mime Type
- Custom Mime Type
- Email Address
- Allow File Discovery
- Binary File
- File Content
- Input Binary Field
- Update Fields
- Keep Revision Forever
- Move to Trash
- OCR Language
- Parent ID
- Use Content As Indexable Text
- Resolve Data
- Email Message
- Enforce Single Parent
- Move To New Owners Root
- Send Notification Email
- Supports All Drives
- Transfer Ownership
- Use Domain Admin Access
- Drive ID
- Can Add Children
- Can Change Copy Requires Writer Permission Restriction
- Can Change Domain Users Only Restriction
- Can Change Drive Background
- Can Change Drive Members Only Restriction
- Can Comment
- Can Copy
- Can Delete Children
- Can Delete Drive
- Can Download
- Can Edit
- Can List Children
- Can Manage Members
- Can Read Revisions
- Can Rename
- Can Rename Drive
- Can Share
- Can Trash Children
- Color RGB
- Created Time
- Admin Managed Restrictions
- Copy Requires Writer Permission
- Domain Users Only
- Drive Members Only
- Return All
- APP Properties
- APP Property

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## CloudFirestore
**Description**: Interact with Google Firebase - Cloud Firestore API
**Credentials**: {
          name: googleFirebaseCloudFirestoreOAuth2Api, required: true, displayOptions: {
            show: {
              authentication: [googleFirebaseCloudFirestoreOAuth2Api
**Actions**:
- Google Cloud Firestore

## RealtimeDatabase
**Description**: Interact with Google Firebase - Realtime Database API
**Credentials**: {
          name: googleFirebaseRealtimeDatabaseOAuth2Api
        }
**Actions**:
- Google Cloud Realtime Database
- Project Name or ID
- Object Path
- Columns / Attributes

## GSuiteAdmin
**Description**: Consume Google Workspace Admin API
**Credentials**: {
          name: gSuiteAdminOAuth2Api, required: true
        }
**Actions**:
- Google Workspace Admin

## Gmail
**Description**: Consume the Gmail API
**Credentials**: None
**Actions**:


## Gmail
**Description**: Fetches emails from Gmail and starts the workflow on specified polling intervals.
**Credentials**: {
          name: googleApi, required: true, displayOptions: {
            show: {
              authentication: [serviceAccount
**Actions**:
- Gmail Trigger
- Include Spam and Trash
- Include Drafts
- Label Names or IDs
- Read Status
- Attachment Prefix
- Download Attachments

## v1
**Description**: Consume the Gmail API
**Credentials**: {
      name: googleApi, required: true, displayOptions: {
        show: {
          authentication: [serviceAccount
**Actions**:


## v2
**Description**: Consume the Gmail API
**Credentials**: {
      name: googleApi, required: true, displayOptions: {
        show: {
          authentication: [serviceAccount
**Actions**:


## Perspective
**Description**: Consume Google Perspective API
**Credentials**: {
          name: googlePerspectiveOAuth2Api, required: true
        }
**Actions**:
- Google Perspective
- Attributes to Analyze
- Attribute Name
- Score Threshold
- Language Name or ID

## Sheet
**Description**: Read, update and write data to Google Sheets
**Credentials**: None
**Actions**:
- Google Sheets

## Sheet
**Description**: Starts the workflow when Google Sheets events occur
**Credentials**: {
          name: googleSheetsTriggerOAuth2Api, required: true, displayOptions: {
            show: {
              authentication: [triggerOAuth2
**Actions**:
- Google Sheets Trigger
- From List
- By URL
- By ID
- Trigger On
- Include in Output
- Columns to Watch
- Data Location on Sheet
- Range Definition
- Header Row
- First Data Row
- Value Render
- DateTime Render

## v1
**Description**: No description
**Credentials**: None
**Actions**:


## v2
**Description**: No description
**Credentials**: None
**Actions**:


## Slides
**Description**: Consume the Google Slides API
**Credentials**: {
          name: googleApi, required: true, displayOptions: {
            show: {
              authentication: [serviceAccount
**Actions**:
- Google Slides
- Presentation ID
- Return All
- Page Object ID
- Texts To Replace
- Match Case
- Slide Names or IDs
- Search For
- Replace With
- Revision ID
- Put Output File in Field

## Task
**Description**: Consume Google Tasks API
**Credentials**: {
          name: googleTasksOAuth2Api, required: true
        }
**Actions**:
- Google Tasks

## Translate
**Description**: Translate data using Google Translate
**Credentials**: {
          name: googleApi, required: true, displayOptions: {
            show: {
              authentication: [serviceAccount
**Actions**:
- Google Translate
- Translate To

## YouTube
**Description**: Consume YouTube API
**Credentials**: {
          name: youTubeOAuth2Api, required: true
        }
**Actions**:
- YouTube

## Gotify
**Description**: Consume Gotify API
**Credentials**: {
          name: gotifyApi, required: true
        }
**Actions**:
- Additional Fields
- Content Type
- Message ID
- Return All

## Grafana
**Description**: Consume the Grafana API
**Credentials**: {
          name: grafanaApi, required: true
        }
**Actions**:


## GraphQL
**Description**: Makes a GraphQL request and returns the received data
**Credentials**: {
          name: httpBasicAuth, required: true, displayOptions: {
            show: {
              authentication: [basicAuth
**Actions**:
- GraphQL
- HTTP Request Method
- Ignore SSL Issues (Insecure)
- Request Format
- Operation Name
- Response Format
- Response Data Property Name

## Grist
**Description**: Consume the Grist API
**Credentials**: {
          name: gristApi, required: true, testedBy: gristApiTest
        }
**Actions**:


## Gumroad
**Description**: Handle Gumroad events via webhooks
**Credentials**: {
          name: gumroadApi, required: true
        }
**Actions**:
- Gumroad Trigger

## HackerNews
**Description**: Consume Hacker News API
**Credentials**: None
**Actions**:
- Hacker News
- Article ID
- Return All
- Additional Fields
- Include Comments

## HaloPSA
**Description**: Consume HaloPSA API
**Credentials**: {
          name: haloPSAApi, required: true, testedBy: haloPSAApiCredentialTest
        }
**Actions**:
- HaloPSA

## Harvest
**Description**: Access data on Harvest
**Credentials**: {
          name: harvestApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- Account Name or ID

## HelpScout
**Description**: Consume Help Scout API
**Credentials**: {
          name: helpScoutOAuth2Api, required: true
        }
**Actions**:
- Help Scout

## HelpScout
**Description**: Starts the workflow when Help Scout events occur
**Credentials**: {
          name: helpScoutOAuth2Api, required: true
        }
**Actions**:
- Help Scout Trigger

## HighLevel
**Description**: Consume HighLevel API
**Credentials**: None
**Actions**:
- HighLevel

## v1
**Description**: Consume HighLevel API v1
**Credentials**: {
      name: highLevelApi, required: true
    }
**Actions**:
- HighLevel

## v2
**Description**: Consume HighLevel API v2
**Credentials**: {
      name: highLevelOAuth2Api, required: true
    }
**Actions**:
- HighLevel

## HomeAssistant
**Description**: Consume Home Assistant API
**Credentials**: {
          name: homeAssistantApi, required: true, testedBy: homeAssistantApiTest
        }
**Actions**:
- Home Assistant

## Html
**Description**: The key under which the extracted value should be saved
**Credentials**: None
**Actions**:
- Extraction Values
- CSS Selector
- Return Value
- Skip Selectors
- Return Array
- HTML
- HTML Template
- <b>Tips</b>: Type ctrl+space for completions. Use <code>{{ }}</code> for expressions and <code>&lt;style&gt;</code> tags for CSS. JS in <code>&lt;script&gt;</code> tags is included but not executed in n8n.
- Source Data
- Input Binary Field
- JSON Property
- Trim Values
- Clean Up Text
- Capitalize Headers
- Custom Styling
- Table Attributes
- Header Attributes
- Row Attributes
- Cell Attributes

## HtmlExtract
**Description**: Extracts data from HTML
**Credentials**: None
**Actions**:
- HTML Extract
- Source Data
- Input Binary Field
- JSON Property
- Extraction Values
- CSS Selector
- Return Value
- Return Array
- Trim Values

## HttpRequest
**Description**: Makes an HTTP request and returns the response data
**Credentials**: None
**Actions**:
- HTTP Request

## V1
**Description**: The way to authenticate
**Credentials**: // ----------------------------------
        //            v1 creds
        // ----------------------------------
        {
          name: httpBasicAuth, required: true, displayOptions: {
            show: {
              authentication: [basicAuth
**Actions**:
- Request Method
- URL
- Ignore SSL Issues (Insecure)
- Response Format
- Property Name
- Put Output File in Field
- JSON/RAW Parameters
- Batch Interval
- Batch Size
- Body Content Type
- Full Response
- Follow All Redirects
- Follow GET/HEAD Redirect
- Ignore Response Code
- MIME Type
- Split Into Items
- Use Querystring
- Send Binary File
- Input Binary Field
- Body Parameters
- Query Parameters
- You can view the raw requests this node makes in your browser

## V2
**Description**: We
**Credentials**: {
          name: httpBasicAuth, required: true, displayOptions: {
            show: {
              authentication: [httpBasicAuth
**Actions**:
- Credential Type
- Generic Auth Type
- Request Method
- URL
- Ignore SSL Issues (Insecure)
- Response Format
- Property Name
- Put Output File in Field
- JSON/RAW Parameters
- Batch Interval
- Batch Size
- Body Content Type
- Full Response
- Follow All Redirects
- Follow GET/HEAD Redirect
- Ignore Response Code
- MIME Type
- Split Into Items
- Use Querystring
- Send Binary File
- Input Binary Field
- Body Parameters
- Query Parameters
- You can view the raw requests this node makes in your browser

## V3
**Description**: Make sure the 
**Credentials**: {
          name: httpSslAuth, required: true, displayOptions: {
            show: {
              provideSslCertificates: [true
**Actions**:


## Hubspot
**Description**: Consume HubSpot API
**Credentials**: None
**Actions**:
- HubSpot

## Hubspot
**Description**: Starts the workflow when HubSpot events occur
**Credentials**: {
          name: hubspotDeveloperApi, required: true
        }
**Actions**:
- HubSpot Trigger
- Property Name or ID
- Additional Fields
- Max Concurrent Requests

## V1
**Description**: Contact VID: ${contactId}
**Credentials**: {
          name: hubspotApi, required: true, testedBy: hubspotApiTest, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:


## V2
**Description**: Contact VID: ${contactId}
**Credentials**: {
          name: hubspotApi, required: true, testedBy: hubspotApiTest, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:


## HumanticAI
**Description**: Consume Humantic AI API
**Credentials**: {
          name: humanticAiApi, required: true
        }
**Actions**:
- Humantic AI

## Hunter
**Description**: Consume Hunter API
**Credentials**: {
          name: hunterApi, required: true
        }
**Actions**:
- Only Emails
- Return All
- First Name
- Last Name

## ICalendar
**Description**: Create iCalendar file
**Credentials**: None
**Actions**:
- iCalendar

## If
**Description**: Route items to different branches (true/false)
**Credentials**: None
**Actions**:


## V1
**Description**: The type of values to compare
**Credentials**: None
**Actions**:
- Value 1
- Value 2
- Date & Time

## V2
**Description**: Whether to ignore letter case when evaluating conditions
**Credentials**: None
**Actions**:
- Ignore Case

## Intercom
**Description**: Consume Intercom API
**Credentials**: {
          name: intercomApi, required: true
        }
**Actions**:


## Interval
**Description**: Triggers the workflow in a given interval
**Credentials**: None
**Actions**:
- This workflow will run on the schedule you define here once you <a data-key=

## InvoiceNinja
**Description**: Consume Invoice Ninja API
**Credentials**: {
          name: invoiceNinjaApi, required: true
        }
**Actions**:
- Invoice Ninja
- API Version

## InvoiceNinja
**Description**: Starts the workflow when Invoice Ninja events occur
**Credentials**: {
          name: invoiceNinjaApi, required: true
        }
**Actions**:
- Invoice Ninja Trigger
- API Version

## ItemLists
**Description**: Helper for working with lists of items and transforming arrays
**Credentials**: None
**Actions**:
- Item Lists

## V1
**Description**: Combine fields into a list in a single new item
**Credentials**: None
**Actions**:
- Field To Split Out
- Fields To Include
- 
- Field Name
- Fields To Aggregate
- Input Field Name
- Rename Field
- Output Field Name
- Put Output in Field
- Fields To Exclude
- Fields To Compare
- Fields To Sort By
- Max Items
- Remove Other Fields
- Disable Dot Notation
- Destination Field Name
- Merge Lists
- Keep Missing And Null Values

## V2
**Description**: Combine fields into a list in a single new item
**Credentials**: None
**Actions**:
- Fields To Split Out
- Fields To Include
- 
- Field Name
- Fields To Aggregate
- Input Field Name
- Rename Field
- Output Field Name
- Put Output in Field
- Fields To Exclude
- Fields To Compare
- Fields To Sort By
- Max Items
- Remove Other Fields
- Disable Dot Notation
- Destination Field Name
- Merge Lists
- Keep Missing And Null Values

## V3
**Description**: No description
**Credentials**: None
**Actions**:


## Iterable
**Description**: Consume Iterable API
**Credentials**: {
          name: iterableApi, required: true
        }
**Actions**:


## Jenkins
**Description**: Consume Jenkins API
**Credentials**: {
          name: jenkinsApi, required: true, testedBy: jenkinApiCredentialTest
        }
**Actions**:
- Make sure the job is setup to support triggering with parameters. <a href=
- Job Name or ID
- Name or ID
- New Job Name
- XML
- To get the XML of an existing job, add \u2018config.xml\u2019 to the end of the job URL
- Instance operation can shutdown Jenkins instance and make it unresponsive. Some commands may not be available depending on instance implementation.
- Return All

## Jira
**Description**: Consume Jira Software API
**Credentials**: {
          name: jiraSoftwareCloudApi, required: true, displayOptions: {
            show: {
              jiraVersion: [cloud
**Actions**:
- Jira Software
- Jira Version

## Jira
**Description**: Starts the workflow when Jira events occur
**Credentials**: {
          displayName: Credentials to Connect to Jira, name: jiraSoftwareCloudApi, required: true, displayOptions: {
            show: {
              jiraVersion: [cloud
**Actions**:
- Jira Trigger
- Credentials to Connect to Jira
- Credentials to Authenticate Webhook
- Jira Version
- Authenticate Incoming Webhook
- Authenticate Webhook With
- Additional Fields
- Exclude Body
- Include Fields

## JotForm
**Description**: Handle JotForm events via webhooks
**Credentials**: {
          name: jotFormApi, required: true
        }
**Actions**:
- JotForm Trigger
- Form Name or ID
- Resolve Data
- Only Answers

## Jwt
**Description**: Be sure to add a valid JWT token to the 
**Credentials**: {
          // eslint-disable-next-line n8n-nodes-base/node-class-description-credentials-name-unsuffixed
          name: jwtAuth, required: true
        }
**Actions**:
- JWT
- Use JSON to Build Payload
- Payload Claims
- Expires In
- JWT ID
- Not Before
- Payload Claims (JSON)
- Return Additional Info
- Ignore Expiration
- Ignore Not Before Claim
- Clock Tolerance
- Key ID
- Override Algorithm

## Kafka
**Description**: Sends messages to a Kafka topic
**Credentials**: {
          name: kafka, required: true, testedBy: kafkaConnectionTest
        }
**Actions**:
- Send Input Data
- JSON Parameters
- Use Schema Registry
- Schema Registry URL
- Use Key
- Event Name
- Headers (JSON)

## Kafka
**Description**: Consume messages from a Kafka topic
**Credentials**: {
          name: kafka, required: true
        }
**Actions**:
- Kafka Trigger
- Group ID
- Use Schema Registry
- Schema Registry URL
- Allow Topic Creation
- Auto Commit Threshold
- Auto Commit Interval
- Heartbeat Interval
- Max Number of Requests
- Read Messages From Beginning
- JSON Parse Message
- Parallel Processing
- Only Message
- Return Headers
- Session Timeout

## Keap
**Description**: Consume Keap API
**Credentials**: {
          name: keapOAuth2Api, required: true
        }
**Actions**:


## Keap
**Description**: Starts the workflow when Infusionsoft events occur
**Credentials**: {
          name: keapOAuth2Api, required: true
        }
**Actions**:
- Keap Trigger
- Event Name or ID
- RAW Data

## Kitemaker
**Description**: Consume the Kitemaker GraphQL API
**Credentials**: {
          name: kitemakerApi, required: true
        }
**Actions**:


## KoBoToolbox
**Description**: Work with KoBoToolbox forms and submissions
**Credentials**: {
          name: koBoToolboxApi, required: true
        }
**Actions**:
- KoBoToolbox

## KoBoToolbox
**Description**: Process KoBoToolbox submissions
**Credentials**: {
          name: koBoToolboxApi, required: true
        }
**Actions**:
- KoBoToolbox Trigger
- Form Name or ID
- Trigger On

## Ldap
**Description**: Interact with LDAP servers
**Credentials**: {
          // eslint-disable-next-line n8n-nodes-base/node-class-description-credentials-name-unsuffixed
          name: ldap, required: true, testedBy: ldapConnectionTest
        }
**Actions**:


## Lemlist
**Description**: Consume the Lemlist API
**Credentials**: None
**Actions**:


## Lemlist
**Description**: Handle Lemlist events via webhooks
**Credentials**: {
          name: lemlistApi, required: true
        }
**Actions**:
- Lemlist Trigger
- Campaign Name or ID
- Is First

## v1
**Description**: Consume the Lemlist API
**Credentials**: {
      name: lemlistApi, required: true
    }
**Actions**:


## v2
**Description**: Consume the Lemlist API
**Credentials**: {
      name: lemlistApi, required: true
    }
**Actions**:


## Line
**Description**: Consume Line API
**Credentials**: {
          name: lineNotifyOAuth2Api, required: true, displayOptions: {
            show: {
              resource: [notification
**Actions**:
- End of service: LINE Notify will be discontinued from April 1st 2025, You can find more information <a href=

## Linear
**Description**: Consume Linear API
**Credentials**: {
          name: linearApi, required: true, testedBy: linearApiTest, displayOptions: {
            show: {
              authentication: [apiToken
**Actions**:


## Linear
**Description**: Starts the workflow when Linear events occur
**Credentials**: {
          name: linearApi, required: true, testedBy: linearApiTest, displayOptions: {
            show: {
              authentication: [apiToken
**Actions**:
- Linear Trigger
- Make sure your credential has the 
- Team Name or ID
- Listen to Resources

## LingvaNex
**Description**: Consume LingvaNex API
**Credentials**: {
          name: lingvaNexApi, required: true
        }
**Actions**:
- LingvaNex
- Translate To
- Additional Options
- Translate Mode

## LinkedIn
**Description**: Consume LinkedIn API
**Credentials**: {
          name: linkedInOAuth2Api, required: true, displayOptions: {
            show: {
              authentication: [standard
**Actions**:
- LinkedIn

## LocalFileTrigger
**Description**: Triggers a workflow on file system changes
**Credentials**: None
**Actions**:
- Local File Trigger
- Trigger On
- File to Watch
- Folder to Watch
- Watch for
- Await Write Finish
- Include Linked Files/Folders
- Ignore Existing Files/Folders
- Max Folder Depth
- Use Polling

## LoneScale
**Description**: Create List, add / delete items
**Credentials**: {
          name: loneScaleApi, required: true
        }
**Actions**:
- LoneScale
- List Name or ID
- First Name
- Last Name
- Company Name
- Additional Fields
- Full Name
- Contact Email
- Current Position
- Company Domain
- Linkedin Url
- Contact Location
- Contact ID

## LoneScale
**Description**: Trigger LoneScale Workflow
**Credentials**: {
          name: loneScaleApi, required: true
        }
**Actions**:
- LoneScale Trigger
- Workflow Name

## MQTT
**Description**: Push messages to MQTT
**Credentials**: {
          name: mqtt, required: true, testedBy: mqttConnectionTest
        }
**Actions**:
- MQTT
- Send Input Data
- QoS

## MQTT
**Description**: Listens to MQTT events
**Credentials**: {
          name: mqtt, required: true
        }
**Actions**:
- MQTT Trigger
- JSON Parse Body
- Only Message
- Parallel Processing

## Magento
**Description**: Consume Magento API
**Credentials**: {
          name: magento2Api, required: true
        }
**Actions**:
- Magento 2

## Mailcheck
**Description**: Consume Mailcheck API
**Credentials**: {
          name: mailcheckApi, required: true
        }
**Actions**:


## Mailchimp
**Description**: Consume Mailchimp API
**Credentials**: {
          name: mailchimpApi, required: true, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:
- List Name or ID
- JSON Parameters
- Email Type
- Opt-in IP
- Signup IP
- Signup Timestamp
- Opt-in Timestamp
- Merge Fields
- Field Name or ID
- Field Value
- Interest Groups
- Category Name or ID
- Category Field ID
- Exclude Fields
- Return All
- Before Last Changed
- Before Timestamp Opt
- Since Last Changed
- Update Fields
- Skip Merge Validation
- Is Syncing
- Group Category Name or ID
- Before Create Time
- Before Send Time
- Exclude Field Names or IDs
- Field Names or IDs
- Since Create Time
- Since Send Time
- Sort Direction
- Sort Field
- Campaign ID

## Mailchimp
**Description**: Handle Mailchimp events via webhooks
**Credentials**: {
          name: mailchimpApi, required: true, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:
- Mailchimp Trigger
- List Name or ID

## MailerLite
**Description**: Consume MailerLite API
**Credentials**: None
**Actions**:
- MailerLite

## MailerLite
**Description**: Starts the workflow when MailerLite events occur
**Credentials**: None
**Actions**:
- MailerLite Trigger

## v1
**Description**: Starts the workflow when MailerLite events occur
**Credentials**: {
          name: mailerLiteApi, required: true
        }
**Actions**:
- MailerLite Trigger

## v1
**Description**: Consume Mailer Lite API
**Credentials**: {
          name: mailerLiteApi, required: true
        }
**Actions**:
- MailerLite

## v2
**Description**: Starts the workflow when MailerLite events occur
**Credentials**: {
          name: mailerLiteApi, required: true
        }
**Actions**:
- MailerLite Trigger

## v2
**Description**: Consume Mailer Lite API
**Credentials**: {
          name: mailerLiteApi, required: true
        }
**Actions**:
- MailerLite

## Mailgun
**Description**: Sends an email via Mailgun
**Credentials**: {
          name: mailgunApi, required: true
        }
**Actions**:
- From Email
- To Email
- Cc Email
- Bcc Email
- HTML

## Mailjet
**Description**: Consume Mailjet API
**Credentials**: {
          name: mailjetEmailApi, required: true, displayOptions: {
            show: {
              resource: [email
**Actions**:


## Mailjet
**Description**: Handle Mailjet events via webhooks
**Credentials**: {
          name: mailjetEmailApi, required: true
        }
**Actions**:
- Mailjet Trigger

## Mandrill
**Description**: Consume Mandrill API
**Credentials**: {
          name: mandrillApi, required: true
        }
**Actions**:
- Template Name or ID
- From Email
- To Email
- JSON Parameters
- Auto Text
- Auto HTML
- BCC Address
- From Name
- Google Analytics Campaign
- Google Analytics Domains
- HTML
- Inline CSS
- Ip Pool
- Preserve Recipients
- Return Path Domain
- Sent At
- Signing Domain
- Track Clicks
- Track Opens
- Tracking Domain
- Url Strip Qs
- View Content Link
- Merge Vars
- Attachments Values
- Attachments Binary

## ManualTrigger
**Description**: Runs the flow on clicking a button in n8n
**Credentials**: None
**Actions**:
- Manual Trigger
- This node is where the workflow execution starts (when you click the \u2018test\u2019 button on the canvas).<br><br> <a data-action=

## Markdown
**Description**: Convert data between Markdown and HTML
**Credentials**: None
**Actions**:
- HTML
- Destination Key
- Bullet Marker
- Code Block Fence
- Emphasis Delimiter
- Global Escape Pattern
- Ignored Elements
- Keep Images With Data
- Line Start Escape Pattern
- Max Consecutive New Lines
- Place URLs At The Bottom
- Strong Delimiter
- Style For Code Block
- Text Replacement Pattern
- Treat As Blocks
- Add Blank To Links
- Automatic Linking to URLs
- Backslash Escapes HTML Tags
- Complete HTML Document
- Customized Header ID
- Emoji Support
- Encode Emails
- Exclude Trailing Punctuation From URLs
- GitHub Code Blocks
- GitHub Compatible Header IDs
- GitHub Mention Link
- GitHub Mentions
- GitHub Task Lists
- Header Level Start
- Mandatory Space Before Header
- Middle Word Asterisks
- Middle Word Underscores
- No Header ID
- Parse Image Dimensions
- Prefix Header ID
- Raw Header ID
- Raw Prefix Header ID
- Simple Line Breaks
- Smart Indentation Fix
- Spaces Indented Sublists
- Split Adjacent Blockquotes
- Tables Header ID
- Tables Support

## Marketstack
**Description**: Consume Marketstack API
**Credentials**: {
          name: marketstackApi, required: true
        }
**Actions**:


## Matrix
**Description**: Consume Matrix API
**Credentials**: {
          name: matrixApi, required: true
        }
**Actions**:


## Mattermost
**Description**: Sends data to Mattermost
**Credentials**: None
**Actions**:


## v1
**Description**: No description
**Credentials**: None
**Actions**:


## Mautic
**Description**: Consume Mautic API
**Credentials**: {
          name: mauticApi, required: true, displayOptions: {
            show: {
              authentication: [credentials
**Actions**:


## Mautic
**Description**: Handle Mautic events via webhooks
**Credentials**: {
          name: mauticApi, required: true, displayOptions: {
            show: {
              authentication: [credentials
**Actions**:
- Mautic Trigger
- Event Names or IDs
- Events Order

## Medium
**Description**: Consume Medium API
**Credentials**: {
          name: mediumApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- Publication Name or ID
- Content Format
- Additional Fields
- Canonical Url
- Notify Followers
- Publish Status
- Return All

## Merge
**Description**: Merges data of multiple streams once data from both is available
**Credentials**: None
**Actions**:


## v1
**Description**: Combines data of both inputs. The output will contain items of input 1 and input 2.
**Credentials**: None
**Actions**:
- Property Input 1
- Property Input 2
- Output Data

## v2
**Description**: All items of input 1, then all items of input 2
**Credentials**: None
**Actions**:
- Combination Mode
- Fields to Match
- Input 1 Field
- Input 2 Field
- Output Type
- Output Data From

## v3
**Description**: No description
**Credentials**: None
**Actions**:


## MessageBird
**Description**: Sends SMS via MessageBird
**Credentials**: {
          name: messageBirdApi, required: true
        }
**Actions**:
- MessageBird
- Additional Fields
- Created Date-Time
- Group IDs
- Message Type
- Report Url
- Scheduled Date-Time
- Type Details

## Metabase
**Description**: Use the Metabase API
**Credentials**: {
          name: metabaseApi, required: true
        }
**Actions**:


## AzureCosmosDb
**Description**: Interact with Azure Cosmos DB API
**Credentials**: {
          name: microsoftAzureCosmosDbSharedKeyApi, required: true
        }
**Actions**:
- Azure Cosmos DB

## Dynamics
**Description**: Consume Microsoft Dynamics CRM API
**Credentials**: {
          name: microsoftDynamicsOAuth2Api, required: true
        }
**Actions**:
- Microsoft Dynamics CRM

## Entra
**Description**: Interact with Micosoft Entra ID API
**Credentials**: {
          name: microsoftEntraOAuth2Api, required: true
        }
**Actions**:
- Microsoft Entra ID

## Excel
**Description**: Consume Microsoft Excel API
**Credentials**: None
**Actions**:
- Microsoft Excel 365

## v1
**Description**: Consume Microsoft Excel API
**Credentials**: {
      name: microsoftExcelOAuth2Api, required: true
    }
**Actions**:
- Microsoft Excel

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## GraphSecurity
**Description**: Consume the Microsoft Graph Security API
**Credentials**: {
          name: microsoftGraphSecurityOAuth2Api, required: true
        }
**Actions**:
- Microsoft Graph Security

## OneDrive
**Description**: Consume Microsoft OneDrive API
**Credentials**: {
          name: microsoftOneDriveOAuth2Api, required: true
        }
**Actions**:
- Microsoft OneDrive

## OneDrive
**Description**: Trigger for Microsoft OneDrive API.
**Credentials**: {
          name: microsoftOneDriveOAuth2Api, required: true
        }
**Actions**:
- Microsoft OneDrive Trigger

## Outlook
**Description**: Consume Microsoft Outlook API
**Credentials**: None
**Actions**:
- Microsoft Outlook

## Outlook
**Description**: Fetches emails from Microsoft Outlook and starts the workflow on specified polling intervals.
**Credentials**: {
          name: microsoftOutlookOAuth2Api, required: true
        }
**Actions**:
- Microsoft Outlook Trigger
- Trigger On

## v1
**Description**: Consume Microsoft Outlook API
**Credentials**: {
      name: microsoftOutlookOAuth2Api, required: true
    }
**Actions**:
- Microsoft Outlook

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## Sql
**Description**: Get, add and update data in Microsoft SQL
**Credentials**: {
          name: microsoftSql, required: true, testedBy: microsoftSqlConnectionTest
        }
**Actions**:
- Microsoft SQL
- Update Key
- Delete Key

## Storage
**Description**: Interact with Azure Storage API
**Credentials**: {
          name: azureStorageOAuth2Api, required: true, displayOptions: {
            show: {
              authentication: [oAuth2
**Actions**:
- Azure Storage

## Teams
**Description**: Consume Microsoft Teams API
**Credentials**: None
**Actions**:
- Microsoft Teams

## v1
**Description**: Consume Microsoft Teams API
**Credentials**: {
      name: microsoftTeamsOAuth2Api, required: true
    }
**Actions**:
- Microsoft Teams

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## ToDo
**Description**: Consume Microsoft To Do API.
**Credentials**: {
          name: microsoftToDoOAuth2Api, required: true
        }
**Actions**:
- Microsoft To Do

## Mindee
**Description**: Consume Mindee API
**Credentials**: {
          name: mindeeReceiptApi, required: true, displayOptions: {
            show: {
              resource: [receipt
**Actions**:
- API Version
- Input Binary Field
- RAW Data

## Misp
**Description**: Consume the MISP API
**Credentials**: {
          name: mispApi, required: true
        }
**Actions**:
- MISP

## Mocean
**Description**: Send SMS and voice messages via Mocean
**Credentials**: {
          name: moceanApi, required: true, testedBy: moceanApiTest
        }
**Actions**:
- Delivery Report URL

## MondayCom
**Description**: Consume Monday.com API
**Credentials**: {
          name: mondayComApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- Monday.com

## MongoDb
**Description**: Find, insert and update documents in MongoDB
**Credentials**: {
          name: mongoDb, required: true, testedBy: mongoDbCredentialTest
        }
**Actions**:
- MongoDB

## MonicaCrm
**Description**: Consume the Monica CRM API
**Credentials**: {
          name: monicaCrmApi, required: true
        }
**Actions**:
- Monica CRM

## MoveBinaryData
**Description**: Move data between binary and JSON properties
**Credentials**: None
**Actions**:
- Convert to/from binary data
- Set All Data
- Source Key
- Destination Key
- Convert All Data
- Add Byte Order Mark (BOM)
- Data Is Base64
- Strip BOM
- File Name
- JSON Parse
- Keep Source
- Keep As Base64
- MIME Type
- Use Raw Data

## Msg91
**Description**: Sends transactional SMS via MSG91
**Credentials**: {
          name: msg91Api, required: true
        }
**Actions**:
- MSG91
- Sender ID

## MySql
**Description**: Get, add and update data in MySQL
**Credentials**: None
**Actions**:
- MySQL

## v1
**Description**: Get, add and update data in MySQL
**Credentials**: {
      name: mySql, required: true, testedBy: mysqlConnectionTest
    }
**Actions**:
- MySQL
- From List
- Update Key

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## N8n
**Description**: Handle events and perform actions on your n8n instance
**Credentials**: {
          name: n8nApi, required: true
        }
**Actions**:
- n8n

## N8nTrainingCustomerDatastore
**Description**: Dummy node used for n8n training
**Credentials**: None
**Actions**:
- Customer Datastore (n8n training)
- Return All

## N8nTrainingCustomerMessenger
**Description**: Dummy node used for n8n training
**Credentials**: None
**Actions**:
- Customer Messenger (n8n training)
- Customer ID

## N8nTrigger
**Description**: Handle events and perform actions on your n8n instance
**Credentials**: None
**Actions**:
- n8n Trigger

## Nasa
**Description**: Retrieve data from the NASA API
**Credentials**: {
          name: nasaApi, required: true
        }
**Actions**:
- NASA
- Asteroid ID
- Additional Fields
- Include Close Approach Data
- Download Image
- Put Output File in Field
- Start Date
- End Date
- Return All

## Netlify
**Description**: Consume Netlify API
**Credentials**: {
          name: netlifyApi, required: true
        }
**Actions**:


## Netlify
**Description**: Handle netlify events via webhooks
**Credentials**: {
          name: netlifyApi, required: true
        }
**Actions**:
- Netlify Trigger
- Site Name or ID
- Form Name or ID

## ADC
**Description**: Consume Netscaler ADC API
**Credentials**: {
          name: citrixAdcApi, required: true
        }
**Actions**:
- Netscaler ADC

## NextCloud
**Description**: Access data on Nextcloud
**Credentials**: {
          name: nextCloudApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- From Path
- To Path
- Delete Path
- File Path
- Put Output File in Field
- Binary File
- File Content
- Input Binary Field
- Share Type
- Circle ID
- Group ID
- Folder Path
- Additional Fields
- Display Name
- Return All
- Update Fields

## NoOp
**Description**: No Operation
**Credentials**: None
**Actions**:
- No Operation, do nothing

## NocoDB
**Description**: Read, update, write and delete data from NocoDB
**Credentials**: {
          name: nocoDb, required: true, displayOptions: {
            show: {
              authentication: [nocoDb
**Actions**:
- NocoDB
- API Version

## Notion
**Description**: Consume Notion API
**Credentials**: None
**Actions**:


## Notion
**Description**: Starts the workflow when Notion events occur
**Credentials**: {
          name: notionApi, required: true
        }
**Actions**:
- Notion Trigger
- In Notion, make sure to <a href=
- ID

## v1
**Description**: Timezone set in n8n
**Credentials**: None
**Actions**:


## v2
**Description**: No description
**Credentials**: None
**Actions**:


## Npm
**Description**: Consume NPM registry API
**Credentials**: {
          name: npmApi, required: false
        }
**Actions**:


## Odoo
**Description**: Consume Odoo API
**Credentials**: {
          name: odooApi, required: true, testedBy: odooApiTest
        }
**Actions**:


## Okta
**Description**: Use the Okta API
**Credentials**: {
          name: oktaApi, required: true
        }
**Actions**:


## OneSimpleApi
**Description**: A toolbox of no-code utilities
**Credentials**: {
          name: oneSimpleApi, required: true
        }
**Actions**:
- One Simple API
- Webpage URL
- Download PDF?
- Put Output In Field
- Page Size
- Force Refresh
- QR Content
- Download Image?
- Download Screenshot?
- Screen Size
- Full Page
- Profile Name
- Artist Name
- From Currency
- To Currency
- Link To Image
- Include Headers?
- Email Address
- URL

## Onfleet
**Description**: Consume Onfleet API
**Credentials**: {
          name: onfleetApi, required: true, testedBy: onfleetApiTest
        }
**Actions**:


## Onfleet
**Description**: Starts the workflow when Onfleet events occur
**Credentials**: {
          name: onfleetApi, required: true, testedBy: onfleetApiTest
        }
**Actions**:
- Onfleet Trigger

## OpenAi
**Description**: Consume Open AI
**Credentials**: {
          name: openAiApi, required: true
        }
**Actions**:
- OpenAI

## OpenThesaurus
**Description**: Get synonmns for German words using the OpenThesaurus API
**Credentials**: None
**Actions**:
- OpenThesaurus
- Starts With
- Substring From Results
- Substring Max Results

## OpenWeatherMap
**Description**: Gets current and future weather information
**Credentials**: {
          name: openWeatherMapApi, required: true
        }
**Actions**:
- OpenWeatherMap
- Location Selection
- City ID
- Zip Code

## Orbit
**Description**: Consume Orbit API
**Credentials**: {
          name: orbitApi, required: true
        }
**Actions**:
- Orbit has been shutdown and will no longer function from July 11th, You can read more <a target=

## Oura
**Description**: Consume Oura API
**Credentials**: {
          name: ouraApi, required: true
        }
**Actions**:


## Paddle
**Description**: Consume Paddle API
**Credentials**: {
          name: paddleApi, required: true
        }
**Actions**:


## PagerDuty
**Description**: Consume PagerDuty API
**Credentials**: {
          name: pagerDutyApi, required: true, displayOptions: {
            show: {
              authentication: [apiToken
**Actions**:
- PagerDuty

## PayPal
**Description**: Consume PayPal API
**Credentials**: {
          name: payPalApi, required: true, testedBy: payPalApiTest
        }
**Actions**:
- PayPal

## PayPal
**Description**: Handle PayPal events via webhooks
**Credentials**: {
          name: payPalApi, required: true
        }
**Actions**:
- PayPal Trigger
- Event Names or IDs

## Peekalink
**Description**: Consume the Peekalink API
**Credentials**: {
          name: peekalinkApi, required: true
        }
**Actions**:
- URL

## Phantombuster
**Description**: Consume Phantombuster API
**Credentials**: {
          name: phantombusterApi, required: true
        }
**Actions**:


## PhilipsHue
**Description**: Consume Philips Hue API
**Credentials**: {
          name: philipsHueOAuth2Api, required: true
        }
**Actions**:
- Philips Hue

## Pipedrive
**Description**: Create and edit data in Pipedrive
**Credentials**: {
          name: pipedriveApi, required: true, displayOptions: {
            show: {
              authentication: [apiToken
**Actions**:
- Additional Fields
- Deal ID
- Due Date
- Organization Name or ID
- Person ID
- User Name or ID
- Custom Properties
- Property Name
- Property Value
- Activity ID
- Update Fields
- Busy Flag
- Public Description
- Associate With
- Organization ID
- Property Name or ID
- Label Name or ID
- Lost Reason
- Stage Name or ID
- Visible To
- Deal Name or ID
- Product Name or ID
- Item Price
- Discount Percentage
- Product Variation ID
- Product Attachment Name or ID
- Exact Match
- Return All
- Include Fields
- Search Fields
- Input Binary Field
- Product ID
- File ID
- Put Output File in Field
- Expected Close Date
- Label Names or IDs
- Owner Name or ID
- Value Properties
- Lead ID
- Person Name or ID
- Note ID
- RAW Data
- Owner ID
- Marketing Status
- Resolve Properties
- Encode Properties
- Exclude Activity IDs
- Archived Status
- First Char
- Predefined Filter Name or ID
- End Date
- Star Date
- Type Names or IDs

## Pipedrive
**Description**: Starts the workflow when Pipedrive events occur
**Credentials**: {
          name: pipedriveApi, required: true, displayOptions: {
            show: {
              authentication: [apiToken
**Actions**:
- Pipedrive Trigger
- Incoming Authentication

## Plivo
**Description**: Send SMS/MMS messages or make phone calls
**Credentials**: {
          name: plivoApi, required: true
        }
**Actions**:


## PostBin
**Description**: Consume PostBin API
**Credentials**: None
**Actions**:
- PostBin

## PostHog
**Description**: Consume PostHog API
**Credentials**: {
          name: postHogApi, required: true
        }
**Actions**:
- PostHog

## Postgres
**Description**: Get, add and update data in Postgres
**Credentials**: None
**Actions**:


## Postgres
**Description**: Listens to Postgres messages
**Credentials**: {
          name: postgres, required: true
        }
**Actions**:
- Postgres Trigger
- Listen For
- Schema Name
- From List
- Table Name
- Channel Name
- Event to listen for
- Additional Fields
- Function Name
- Replace if Exists
- Trigger Name
- Connection Timeout
- Delay Closing Idle Connection

## v1
**Description**: Get, add and update data in Postgres
**Credentials**: {
      name: postgres, required: true, testedBy: postgresConnectionTest
    }
**Actions**:
- Update Key
- Return Fields
- Additional Fields
- Output Large-Format Numbers As
- Query Parameters

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## Postmark
**Description**: Starts the workflow when Postmark events occur
**Credentials**: {
          name: postmarkApi, required: true
        }
**Actions**:
- Postmark Trigger
- First Open
- Include Content

## ProfitWell
**Description**: Consume ProfitWell API
**Credentials**: {
          name: profitWellApi, required: true
        }
**Actions**:
- ProfitWell

## Pushbullet
**Description**: Consume Pushbullet API
**Credentials**: {
          name: pushbulletOAuth2Api, required: true
        }
**Actions**:
- URL
- Input Binary Field
- Value Name or ID
- Push ID
- Return All
- Modified After

## Pushcut
**Description**: Consume Pushcut API
**Credentials**: {
          name: pushcutApi, required: true
        }
**Actions**:
- Notification Name or ID
- Additional Fields
- Device Names or IDs

## Pushcut
**Description**: Starts the workflow when Pushcut events occur
**Credentials**: {
          name: pushcutApi, required: true
        }
**Actions**:
- Pushcut Trigger
- Action Name

## Pushover
**Description**: Consume Pushover API
**Credentials**: {
          name: pushoverApi, required: true
        }
**Actions**:
- User Key
- Retry (Seconds)
- Expire (Seconds)
- Additional Fields
- Attachment Property
- Input Binary Field
- HTML Formatting
- Sound Name or ID
- URL
- URL Title

## QuestDb
**Description**: Get, add and update data in QuestDB
**Credentials**: {
          name: questDb, required: true
        }
**Actions**:
- QuestDB
- Return Fields
- Additional Fields
- Query Parameters

## QuickBase
**Description**: Integrate with the Quick Base RESTful API
**Credentials**: {
          name: quickbaseApi, required: true
        }
**Actions**:
- Quick Base

## QuickBooks
**Description**: Consume the QuickBooks Online API
**Credentials**: {
          name: quickBooksOAuth2Api, required: true
        }
**Actions**:
- QuickBooks Online

## QuickChart
**Description**: Create a chart via QuickChart
**Credentials**: None
**Actions**:
- QuickChart
- Chart Type
- Add Labels
- Labels Array
- Put Output In Field
- Chart Options
- Background Color
- Device Pixel Ratio
- Dataset Options
- Border Color
- Point Style

## RabbitMQ
**Description**: Sends messages to a RabbitMQ topic
**Credentials**: {
          name: rabbitmq, required: true, testedBy: rabbitmqConnectionTest
        }
**Actions**:
- RabbitMQ
- Will delete an item from the queue triggered earlier in the workflow by a RabbitMQ Trigger node
- Queue / Topic
- Routing Key
- Send Input Data
- Alternate Exchange
- Auto Delete Queue

## RabbitMQ
**Description**: Listens to RabbitMQ messages
**Credentials**: {
          name: rabbitmq, required: true
        }
**Actions**:
- RabbitMQ Trigger
- Queue / Topic
- Content Is Binary
- Delete From Queue When
- JSON Parse Body
- Only Content
- Parallel Message Processing Limit
- RoutingKey
- To delete an item from the queue, insert a RabbitMQ node later in the workflow and use the 

## Raindrop
**Description**: Consume the Raindrop API
**Credentials**: {
          name: raindropOAuth2Api, required: true
        }
**Actions**:


## ReadBinaryFile
**Description**: Reads a binary file from disk
**Credentials**: None
**Actions**:
- Read Binary File
- File Path
- Property Name

## ReadBinaryFiles
**Description**: Reads binary files from disk
**Credentials**: None
**Actions**:
- Read Binary Files
- File Selector
- Property Name

## ReadPdf
**Description**: Reads a PDF and extracts its content
**Credentials**: None
**Actions**:
- Read PDF
- Input Binary Field

## Reddit
**Description**: Consume the Reddit API
**Credentials**: {
          name: redditOAuth2Api, required: true, displayOptions: {
            show: {
              resource: [postComment, post, profile
**Actions**:


## Redis
**Description**: Get, send and update data in Redis
**Credentials**: {
          name: redis, required: true, testedBy: redisConnectionTest
        }
**Actions**:
- Key Type
- Dot Notation
- TTL
- Key Pattern
- Get Values
- Value Is JSON

## Redis
**Description**: Subscribe to redis channel
**Credentials**: {
          name: redis, required: true, testedBy: redisConnectionTest
        }
**Actions**:
- Redis Trigger
- JSON Parse Body
- Only Message

## RenameKeys
**Description**: Update item field names
**Credentials**: None
**Actions**:
- Rename Keys
- Current Key Name
- New Key Name
- Additional Options
- Be aware that by using regular expression previously renamed keys can be affected
- Regular Expression
- Replace With
- Case Insensitive
- Max Depth

## RespondToWebhook
**Description**: Respond with all input JSON items
**Credentials**: {
          name: jwtAuth, required: true, displayOptions: {
            show: {
              respondWith: [jwt
**Actions**:
- Respond With
- Respond to Webhook
- Verify that the 
- When using expressions, note that this node will only run for the first item in the input data
- Redirect URL
- Response Body
- Response Data Source
- Input Field Name
- Response Code
- Response Headers
- Put Response in Field

## Rocketchat
**Description**: Consume RocketChat API
**Credentials**: {
          name: rocketchatApi, required: true
        }
**Actions**:
- RocketChat
- JSON Parameters
- Thumb URL
- Message Link
- Author Name
- Author Link
- Author Icon
- Title Link
- Title Link Download
- Image URL
- Audio URL
- Video URL

## RssFeedRead
**Description**: Reads data from an RSS Feed
**Credentials**: None
**Actions**:
- RSS Read
- URL
- Ignore SSL Issues (Insecure)

## RssFeedRead
**Description**: Starts a workflow when an RSS feed is updated
**Credentials**: None
**Actions**:
- RSS Feed Trigger
- Feed URL

## Rundeck
**Description**: Manage Rundeck API
**Credentials**: {
          name: rundeckApi, required: true
        }
**Actions**:
- Job ID

## S3
**Description**: Sends data to any S3-compatible service
**Credentials**: {
          name: s3, required: true
        }
**Actions**:
- S3
- This node is for services that use the S3 standard, e.g. Minio or Digital Ocean Spaces. For AWS S3 use the 

## Salesforce
**Description**: Consume Salesforce API
**Credentials**: {
          name: salesforceOAuth2Api, required: true, displayOptions: {
            show: {
              authentication: [oAuth2
**Actions**:


## Salesforce
**Description**: Fetches data from Salesforce and starts the workflow on specified polling intervals.
**Credentials**: {
          name: salesforceOAuth2Api, required: true
        }
**Actions**:
- Salesforce Trigger
- Trigger On
- Custom Object Name or ID

## Salesmate
**Description**: Consume Salesmate API
**Credentials**: {
          name: salesmateApi, required: true
        }
**Actions**:


## Schedule
**Description**: Triggers the workflow on a given schedule
**Credentials**: None
**Actions**:
- Schedule Trigger
- This workflow will run on the schedule you define here once you <a data-key=
- Trigger Rules
- Trigger Interval
- Seconds Between Triggers
- Minutes Between Triggers
- Hours Between Triggers
- Days Between Triggers
- Weeks Between Triggers
- Months Between Triggers
- Trigger at Day of Month
- Trigger on Weekdays
- Trigger at Hour
- 1am
- 2am
- 3am
- 4am
- 5am
- 6am
- 7am
- 8am
- 9am
- 10am
- 11am
- 1pm
- 2pm
- 3pm
- 4pm
- 5pm
- 6pm
- 7pm
- 8pm
- 9pm
- 10pm
- 11pm
- Trigger at Minute
- You can find help generating your cron expression <a href=

## SeaTable
**Description**: Read, update, write and delete data from SeaTable
**Credentials**: None
**Actions**:
- SeaTable

## SeaTable
**Description**: Starts the workflow when SeaTable events occur
**Credentials**: None
**Actions**:
- SeaTable Trigger

## v1
**Description**: Consume the SeaTable API
**Credentials**: {
      name: seaTableApi, required: true
    }
**Actions**:
- SeaTable

## v1
**Description**: The name of SeaTable table to access. Choose from the list, or specify an ID using an <a href=
**Credentials**: {
          name: seaTableApi, required: true
        }
**Actions**:
- Table Name or ID

## v1
**Description**: No description
**Credentials**: None
**Actions**:


## v2
**Description**: Trigger on newly created rows
**Credentials**: {
          name: seaTableApi, required: true
        }
**Actions**:
- Table Name
- View Name
- Signature Column
- Return Column Names
- 

## v2
**Description**: No description
**Credentials**: None
**Actions**:


## actions
**Description**: Consume the SeaTable API
**Credentials**: {
      name: seaTableApi, required: true
    }
**Actions**:
- SeaTable

## SecurityScorecard
**Description**: Consume SecurityScorecard API
**Credentials**: {
          name: securityScorecardApi, required: true
        }
**Actions**:
- SecurityScorecard

## Segment
**Description**: Consume Segment API
**Credentials**: {
          name: segmentApi, required: true
        }
**Actions**:


## SendGrid
**Description**: Consume SendGrid API
**Credentials**: {
          name: sendGridApi, required: true
        }
**Actions**:
- SendGrid

## Sendy
**Description**: Consume Sendy API
**Credentials**: {
          name: sendyApi, required: true
        }
**Actions**:


## SentryIo
**Description**: Consume Sentry.io API
**Credentials**: {
          name: sentryIoOAuth2Api, required: true, displayOptions: {
            show: {
              authentication: [oAuth2
**Actions**:
- Sentry.io
- Sentry Version

## ServiceNow
**Description**: Consume ServiceNow API
**Credentials**: {
          name: serviceNowOAuth2Api, required: true, displayOptions: {
            show: {
              authentication: [oAuth2
**Actions**:
- ServiceNow

## Set
**Description**: Add or edit fields on an input item and optionally remove other fields
**Credentials**: None
**Actions**:


## v1
**Description**: Sets values on items and optionally remove other values
**Credentials**: None
**Actions**:
- Keep Only Set
- Values to Set
- Dot Notation

## v2
**Description**: Modify, add, or remove item fields
**Credentials**: None
**Actions**:
- Edit Fields (Set)
- Duplicate Item
- Duplicate Item Count
- Item duplication is set in the node settings. This option will be ignored when the workflow runs automatically.
- Include in Output
- Include Other Input Fields
- Input Fields to Include
- Fields to Include
- Fields to Exclude
- Include Binary File
- Strip Binary Data
- Ignore Type Conversion Errors
- Support Dot Notation

## Shopify
**Description**: Consume Shopify API
**Credentials**: {
          name: shopifyApi, required: true, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:
- Shopify API Version: 2024-07

## Shopify
**Description**: Handle Shopify events via webhooks
**Credentials**: {
          name: shopifyApi, required: true, displayOptions: {
            show: {
              authentication: [apiKey
**Actions**:
- Shopify Trigger
- Trigger On

## Signl4
**Description**: Consume SIGNL4 API
**Credentials**: {
          name: signl4Api, required: true
        }
**Actions**:
- SIGNL4
- Additional Fields
- Alerting Scenario
- Attachments Binary
- Property Name
- External ID

## Simulate
**Description**: Simulate a node
**Credentials**: None
**Actions**:
- Number of Items

## Simulate
**Description**: Simulate a trigger node
**Credentials**: None
**Actions**:
- Simulate Trigger
- Output (JSON)

## Slack
**Description**: Consume Slack API
**Credentials**: None
**Actions**:


## Slack
**Description**: Handle Slack events via webhooks
**Credentials**: {
          name: slackApi, required: true
        }
**Actions**:
- Slack Trigger
- Set up a webhook in your Slack app to enable this node. <a href=
- Trigger On
- Watch Whole Workspace
- This will use one execution for every event in any channel your bot is in, use with caution
- Channel to Watch
- From List
- By ID
- By URL
- Download Files
- Resolve IDs
- Usernames or IDs to Ignore

## V1
**Description**: No description
**Credentials**: {
          name: slackApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:


## V2
**Description**: No description
**Credentials**: {
          name: slackApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:


## Sms77
**Description**: Send SMS and make text-to-speech calls
**Credentials**: {
          name: sms77Api, required: true
        }
**Actions**:
- seven
- Foreign ID
- Performance Tracking
- TTL

## Snowflake
**Description**: Get, add and update data in Snowflake
**Credentials**: {
          name: snowflake, required: true
        }
**Actions**:
- Update Key

## SplitInBatches
**Description**: Split data into batches and iterate over each batch
**Credentials**: None
**Actions**:
- Split In Batches

## v1
**Description**: Split data into batches and iterate over each batch
**Credentials**: None
**Actions**:
- Split In Batches
- You may not need this node \u2014 n8n nodes automatically run once for each input item. <a href=
- Batch Size

## v2
**Description**: Split data into batches and iterate over each batch
**Credentials**: None
**Actions**:
- Split In Batches
- You may not need this node \u2014 n8n nodes automatically run once for each input item. <a href=
- Batch Size

## v3
**Description**: Split data into batches and iterate over each batch
**Credentials**: None
**Actions**:
- Loop Over Items (Split in Batches)
- You may not need this node \u2014 n8n nodes automatically run once for each input item. <a href=
- Batch Size

## Splunk
**Description**: Consume the Splunk Enterprise API
**Credentials**: None
**Actions**:


## v1
**Description**: Consume the Splunk Enterprise API
**Credentials**: {
      name: splunkApi, required: true
    }
**Actions**:


## v2
**Description**: No description
**Credentials**: None
**Actions**:


## Spontit
**Description**: Consume Spontit API
**Credentials**: {
          name: spontitApi, required: true
        }
**Actions**:


## Spotify
**Description**: Access public song data via the Spotify API
**Credentials**: {
          name: spotifyOAuth2Api, required: true
        }
**Actions**:
- Resource ID
- Track ID
- Album ID
- Search Keyword
- Artist ID
- Playlist ID
- Additional Fields
- Return All

## SpreadsheetFile
**Description**: Reads and writes data from a spreadsheet file like CSV, XLS, ODS, etc
**Credentials**: None
**Actions**:
- Spreadsheet File

## v1
**Description**: No description
**Credentials**: None
**Actions**:


## v2
**Description**: No description
**Credentials**: None
**Actions**:


## SseTrigger
**Description**: Triggers the workflow when Server-Sent Events occur
**Credentials**: None
**Actions**:
- SSE Trigger
- URL

## Ssh
**Description**: Execute commands via SSH
**Credentials**: {
          name: sshPassword, required: true, testedBy: sshConnectionTest, displayOptions: {
            show: {
              authentication: [password
**Actions**:
- SSH
- Working Directory
- Input Binary Field
- Target Directory
- File Property
- File Name

## Stackby
**Description**: Read, write, and delete data in Stackby
**Credentials**: {
          name: stackbyApi, required: true
        }
**Actions**:
- Stack ID
- ID
- Return All
- Additional Fields

## Start
**Description**: Starts the workflow execution from this node
**Credentials**: None
**Actions**:
- This node is where a manual workflow execution starts. To make one, go back to the canvas and click \u2018execute workflow\u2019

## StickyNote
**Description**: Make your workflow easier to understand
**Credentials**: None
**Actions**:
- Sticky Note

## StopAndError
**Description**: Throw an error in the workflow
**Credentials**: None
**Actions**:
- Stop and Error
- Error Type
- Error Message
- Error Object

## Storyblok
**Description**: Consume Storyblok API
**Credentials**: {
          name: storyblokContentApi, required: true, displayOptions: {
            show: {
              source: [contentApi
**Actions**:


## Strapi
**Description**: Consume Strapi API
**Credentials**: {
          name: strapiApi, required: true, testedBy: strapiApiTest, displayOptions: {
            show: {
              authentication: [password
**Actions**:


## Strava
**Description**: Consume Strava API
**Credentials**: {
          name: stravaOAuth2Api, required: true
        }
**Actions**:


## Strava
**Description**: Starts the workflow when Strava events occur
**Credentials**: {
          name: stravaOAuth2Api, required: true
        }
**Actions**:
- Strava Trigger
- Resolve Data
- Delete If Exist

## Stripe
**Description**: Consume the Stripe API
**Credentials**: {
          name: stripeApi, required: true
        }
**Actions**:


## Stripe
**Description**: Handle Stripe events via webhooks
**Credentials**: {
          name: stripeApi, required: true
        }
**Actions**:
- Stripe Trigger

## Supabase
**Description**: Add, get, delete and update data in a table
**Credentials**: {
          name: supabaseApi, required: true, testedBy: supabaseApiCredentialTest
        }
**Actions**:
- Use Custom Schema

## SurveyMonkey
**Description**: Starts the workflow when Survey Monkey events occur
**Credentials**: {
          name: surveyMonkeyApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- SurveyMonkey Trigger
- Survey Names or IDs
- Survey Name or ID
- Collector Names or IDs
- Resolve Data
- Only Answers

## Switch
**Description**: Route items depending on defined expression or rules
**Credentials**: None
**Actions**:


## V1
**Description**: Expression decides how to route data
**Credentials**: None
**Actions**:
- Data Type
- Value 1
- Routing Rules
- Value 2
- Fallback Output

## V2
**Description**: Expression decides how to route data
**Credentials**: None
**Actions**:
- Outputs Amount
- Data Type
- Value 1
- Routing Rules
- Value 2
- Output Key
- Fallback Output Name or ID

## V3
**Description**: Items will be ignored
**Credentials**: None
**Actions**:
- Number of Outputs
- Output Index
- Routing Rules
- Rename Output
- Output Name
- Fallback Output
- Ignore Case
- Rename Fallback Output
- Send data to all matching outputs

## SyncroMSP
**Description**: Manage contacts, tickets and more from Syncro MSP
**Credentials**: None
**Actions**:
- SyncroMSP

## v1
**Description**: No description
**Credentials**: None
**Actions**:


## Taiga
**Description**: Consume Taiga API
**Credentials**: {
          name: taigaApi, required: true
        }
**Actions**:


## Taiga
**Description**: Handle Taiga events via webhook
**Credentials**: {
          name: taigaApi, required: true
        }
**Actions**:
- Taiga Trigger
- Project Name or ID

## Tapfiliate
**Description**: Consume Tapfiliate API
**Credentials**: {
          name: tapfiliateApi, required: true
        }
**Actions**:


## Telegram
**Description**: Sends data to Telegram
**Credentials**: {
          name: telegramApi, required: true
        }
**Actions**:
- Chat ID
- Message ID
- Additional Fields
- Disable Notification
- User ID
- Query ID
- Cache Time
- Show Alert
- URL
- File ID
- Message Type
- Binary File
- Input Binary Field
- Inline Message ID
- Reply Markup
- Media File
- Parse Mode
- Force Reply
- Inline Keyboard
- Callback Data
- Switch Inline Query Current Chat
- Switch Inline Query
- Web App
- Reply Keyboard
- Request Contact
- Request Location
- Reply Keyboard Options
- Resize Keyboard
- One Time Keyboard
- Reply Keyboard Remove
- Remove Keyboard
- Disable WebPage Preview
- File Name
- Reply To Message ID
- Message Thread ID

## Telegram
**Description**: Starts the workflow on a Telegram update
**Credentials**: {
          name: telegramApi, required: true
        }
**Actions**:
- Telegram Trigger
- Due to Telegram API limitations, you can use just one Telegram trigger for each bot at a time
- Trigger On
- Every uploaded attachment, even if sent in a group, will trigger a separate event. You can identify that an attachment belongs to a certain group by <code>media_group_id</code> .
- Additional Fields
- Download Images/Files
- Image Size
- Restrict to Chat IDs
- Restrict to User IDs

## TheHive
**Description**: Consume TheHive API
**Credentials**: {
          name: theHiveApi, required: true
        }
**Actions**:
- TheHive

## TheHive
**Description**: Starts the workflow when TheHive events occur
**Credentials**: None
**Actions**:
- TheHive Trigger
- You must set up the webhook in TheHive \u2014 instructions <a href=

## TheHiveProject
**Description**: No description
**Credentials**: None
**Actions**:


## TheHiveProject
**Description**: Starts the workflow when TheHive events occur
**Credentials**: None
**Actions**:
- TheHive 5 Trigger
- You must set up the webhook in TheHive \u2014 instructions <a href=
- Output Only Data

## TimescaleDb
**Description**: Add and update data in TimescaleDB
**Credentials**: {
          name: timescaleDb, required: true
        }
**Actions**:
- TimescaleDB
- Update Key
- Return Fields
- Additional Fields
- Query Parameters

## Todoist
**Description**: Consume Todoist API
**Credentials**: None
**Actions**:


## v1
**Description**: Consume Todoist API
**Credentials**: {
      name: todoistApi, required: true, displayOptions: {
        show: {
          authentication: [apiKey
**Actions**:
- Task ID
- Project Name or ID
- From List
- ID
- Section Name or ID
- Label Names or IDs
- Sync Commands
- Additional Fields
- Due Date Time
- Due String Locale
- Due String
- Parent Name or ID
- Return All
- IDs
- Label Name or ID
- Update Fields

## v2
**Description**: Consume Todoist API
**Credentials**: {
      name: todoistApi, required: true, displayOptions: {
        show: {
          authentication: [apiKey
**Actions**:
- Task ID
- Project Name or ID
- From List
- ID
- Section Name or ID
- Additional Fields
- Parent Name or ID
- Label Names or IDs
- Sync Commands
- Due Date Time
- Due String Locale
- Due String
- Return All
- IDs
- Label Name or ID
- Update Fields

## Toggl
**Description**: Starts the workflow when Toggl events occur
**Credentials**: {
          name: togglApi, required: true
        }
**Actions**:
- Toggl Trigger

## Totp
**Description**: Generate a time-based one-time password
**Credentials**: {
          name: totpApi, required: true
        }
**Actions**:
- TOTP

## Aggregate
**Description**: Combine a field from many items into a list in a single item
**Credentials**: None
**Actions**:
- Fields To Aggregate
- 
- Input Field Name
- Rename Field
- Output Field Name
- Put Output in Field
- Fields To Exclude
- Fields To Include
- Disable Dot Notation
- Merge Lists
- Include Binaries
- Keep Only Unique Binaries
- Keep Missing And Null Values

## Limit
**Description**: Restrict the number of items
**Credentials**: None
**Actions**:
- Max Items

## RemoveDuplicates
**Description**: Delete items with matching field values
**Credentials**: None
**Actions**:
- Remove Duplicates

## v1
**Description**: Delete items with matching field values
**Credentials**: None
**Actions**:
- Remove Duplicates
- Fields To Exclude
- Fields To Compare
- Disable Dot Notation
- Remove Other Fields

## v2
**Description**: Delete items with matching field values
**Credentials**: None
**Actions**:
- Remove Duplicates

## Sort
**Description**: Change items order
**Credentials**: None
**Actions**:
- Fields To Sort By
- 
- Field Name
- Disable Dot Notation

## SplitOut
**Description**: Turn a list inside item(s) into separate items
**Credentials**: None
**Actions**:
- Split Out
- Fields To Split Out
- Fields To Include
- Disable Dot Notation
- Destination Field Name
- Include Binary

## Summarize
**Description**: Sum, count, max, etc. across items
**Credentials**: None
**Actions**:
- Fields to Summarize
- 
- Include Empty Values
- Custom Separator
- Fields to Split By
- Fields to Group By
- Continue if Field Not Found
- Disable Dot Notation
- Output Format
- Ignore items without valid fields to group by

## TravisCi
**Description**: Consume TravisCI API
**Credentials**: {
          name: travisCiApi, required: true
        }
**Actions**:
- TravisCI

## Trello
**Description**: Create, change and delete boards and cards
**Credentials**: {
          name: trelloApi, required: true
        }
**Actions**:


## Trello
**Description**: Starts the workflow when Trello events occur
**Credentials**: {
          name: trelloApi, required: true
        }
**Actions**:
- Trello Trigger
- Model ID

## Twake
**Description**: Consume Twake API
**Credentials**: {
          name: twakeCloudApi, required: true
          // displayOptions: {
          // 	show: {
          // 		twakeVersion: [
          // 			cloud, //
**Actions**:
- Twake Version
- Channel Name or ID
- Additional Fields
- Sender Icon
- Sender Name

## Twilio
**Description**: Send SMS and WhatsApp messages or make phone calls
**Credentials**: {
          name: twilioApi, required: true
        }
**Actions**:
- To Whatsapp
- Use TwiML
- Status Callback

## Twilio
**Description**: Starts the workflow on a Twilio update
**Credentials**: {
          name: twilioApi, required: true
        }
**Actions**:
- Twilio Trigger
- Trigger On
- The 

## Twist
**Description**: Consume Twist API
**Credentials**: {
          name: twistOAuth2Api, required: true
        }
**Actions**:


## Twitter
**Description**: Consume the X API
**Credentials**: None
**Actions**:
- X (Formerly Twitter)

## V1
**Description**: Consume Twitter API
**Credentials**: {
          name: twitterOAuth1Api, required: true
        }
**Actions**:


## V2
**Description**: Post, like, and search tweets, send messages, search users, and add users to lists
**Credentials**: {
          name: twitterOAuth2Api, required: true
        }
**Actions**:


## Typeform
**Description**: Starts the workflow on a Typeform form submission
**Credentials**: {
          name: typeformApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- Typeform Trigger
- Form Name or ID
- Simplify Answers
- Only Answers

## UProc
**Description**: Consume uProc API
**Credentials**: {
          name: uprocApi, required: true
        }
**Actions**:
- uProc
- Additional Options
- Data Webhook

## UnleashedSoftware
**Description**: Consume Unleashed Software API
**Credentials**: {
          name: unleashedSoftwareApi, required: true
        }
**Actions**:
- Unleashed Software

## Uplead
**Description**: Consume Uplead API
**Credentials**: {
          name: upleadApi, required: true
        }
**Actions**:


## UptimeRobot
**Description**: Consume UptimeRobot API
**Credentials**: {
          name: uptimeRobotApi, required: true
        }
**Actions**:
- UptimeRobot

## UrlScanIo
**Description**: Provides various utilities for monitoring websites like health checks or screenshots
**Credentials**: {
          name: urlScanIoApi, required: true
        }
**Actions**:
- urlscan.io

## Datacenter
**Description**: Consume Venafi TLS Protect Datacenter
**Credentials**: {
          name: venafiTlsProtectDatacenterApi, required: true
        }
**Actions**:
- Venafi TLS Protect Datacenter

## Datacenter
**Description**: Starts the workflow when Venafi events occur
**Credentials**: {
          name: venafiTlsProtectDatacenterApi, required: true
        }
**Actions**:
- Venafi TLS Protect Datacenter Trigger
- Trigger On

## ProtectCloud
**Description**: Consume Venafi TLS Protect Cloud API
**Credentials**: {
          name: venafiTlsProtectCloudApi, required: true
        }
**Actions**:
- Venafi TLS Protect Cloud

## ProtectCloud
**Description**: Starts the workflow when Venafi events occur
**Credentials**: {
          name: venafiTlsProtectCloudApi, required: true
        }
**Actions**:
- Venafi TLS Protect Cloud Trigger
- Trigger On

## Vero
**Description**: Consume Vero API
**Credentials**: {
          name: veroApi, required: true
        }
**Actions**:


## Vonage
**Description**: Consume Vonage API
**Credentials**: {
          name: vonageApi, required: true
        }
**Actions**:
- Input Binary Field
- UDH
- URL
- Validity (in minutes)
- VCard
- VCal
- Additional Fields
- Account Ref
- Client Ref
- Message Class
- Protocol ID
- Status Report Req
- TTL (in Minutes)

## Wait
**Description**: The time to wait
**Credentials**: None
**Actions**:
- Wait Amount
- Wait Unit
- Limit Wait Time
- Limit Type
- Max Date and Time
- Webhook Suffix
- Date and Time
- The webhook URL will be generated at run time. It can be referenced with the <strong>$execution.resumeUrl</strong> variable. Send it somewhere before getting to this node. <a href=
- The form url will be generated at run time. It can be referenced with the <strong>$execution.resumeFormUrl</strong> variable. Send it somewhere before getting to this node. <a href=

## V1
**Description**: Handle Webflow events via webhooks
**Credentials**: {
          name: webflowApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:
- Webflow Trigger
- Site Name or ID

## V1
**Description**: Consume the Webflow API
**Credentials**: {
          name: webflowApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:


## V2
**Description**: Handle Webflow events via webhooks
**Credentials**: {
          name: webflowOAuth2Api, required: true
        }
**Actions**:
- Webflow Trigger
- Site Name or ID

## V2
**Description**: No description
**Credentials**: None
**Actions**:


## Webflow
**Description**: Consume the Webflow API
**Credentials**: None
**Actions**:


## Webflow
**Description**: Handle Webflow events via webhooks
**Credentials**: None
**Actions**:
- Webflow Trigger

## Webhook
**Description**: Starts the workflow when a webhook is called
**Credentials**: None
**Actions**:
- Allow Multiple HTTP Methods
- HTTP Methods
- Insert a 

## Wekan
**Description**: Consume Wekan API
**Credentials**: {
          name: wekanApi, required: true
        }
**Actions**:


## WhatsApp
**Description**: Access WhatsApp API
**Credentials**: {
          name: WHATSAPP_CREDENTIALS_TYPE, required: true
        }
**Actions**:
- WhatsApp Business Cloud

## WhatsApp
**Description**: Handle WhatsApp events via webhooks
**Credentials**: {
          name: whatsAppTriggerApi, required: true
        }
**Actions**:
- WhatsApp Trigger
- Due to Facebook API limitations, you can use just one WhatsApp trigger for each Facebook App
- Trigger On
- Receive Message Status Updates

## Wise
**Description**: Consume the Wise API
**Credentials**: {
          name: wiseApi, required: true
        }
**Actions**:


## Wise
**Description**: Handle Wise events via webhooks
**Credentials**: {
          name: wiseApi, required: true
        }
**Actions**:
- Wise Trigger
- Profile Name or ID

## WooCommerce
**Description**: Consume WooCommerce API
**Credentials**: {
          name: wooCommerceApi, required: true
        }
**Actions**:
- WooCommerce

## WooCommerce
**Description**: Handle WooCommerce events via webhooks
**Credentials**: {
          name: wooCommerceApi, required: true
        }
**Actions**:
- WooCommerce Trigger

## Wordpress
**Description**: Consume Wordpress API
**Credentials**: {
          name: wordpressApi, required: true
        }
**Actions**:


## Workable
**Description**: Starts the workflow when Workable events occur
**Credentials**: {
          name: workableApi, required: true
        }
**Actions**:
- Workable Trigger
- Trigger On
- Job Name or ID
- Stage Name or ID

## WorkflowTrigger
**Description**: Triggers based on various lifecycle events, like when a workflow is activated
**Credentials**: None
**Actions**:
- Workflow Trigger
- This node is deprecated and would not be updated in the future. Please use 

## WriteBinaryFile
**Description**: Writes a binary file to disk
**Credentials**: None
**Actions**:
- Write Binary File
- File Name
- Property Name

## Wufoo
**Description**: Handle Wufoo events via webhooks
**Credentials**: {
          name: wufooApi, required: true
        }
**Actions**:
- Wufoo Trigger
- Forms Name or ID
- Only Answers

## Xero
**Description**: Consume Xero API
**Credentials**: {
          name: xeroOAuth2Api, required: true
        }
**Actions**:


## Xml
**Description**: Convert data from and to XML
**Credentials**: None
**Actions**:
- XML
- If your XML is inside a binary file, use the 
- Property Name
- Allow Surrogate Chars
- Attribute Key
- Character Key
- Root Name
- Explicit Array
- Explicit Root
- Ignore Attributes
- Merge Attributes
- Normalize Tags

## Yourls
**Description**: Consume Yourls API
**Credentials**: {
          name: yourlsApi, required: true
        }
**Actions**:


## Zammad
**Description**: Consume the Zammad API
**Credentials**: {
          name: zammadBasicAuthApi, required: true, testedBy: zammadBasicAuthApiTest, displayOptions: {
            show: {
              authentication: [basicAuth
**Actions**:


## Zendesk
**Description**: Consume Zendesk API
**Credentials**: {
          name: zendeskApi, required: true, displayOptions: {
            show: {
              authentication: [apiToken
**Actions**:


## Zendesk
**Description**: Handle Zendesk events via webhooks
**Credentials**: {
          name: zendeskApi, required: true, displayOptions: {
            show: {
              authentication: [apiToken
**Actions**:
- Zendesk Trigger
- Field Names or IDs

## Zoho
**Description**: Consume Zoho CRM API
**Credentials**: {
          name: zohoOAuth2Api, required: true
        }
**Actions**:
- Zoho CRM

## Zoom
**Description**: Consume Zoom API
**Credentials**: {
          // create a JWT app on Zoom Marketplace
          //https://marketplace.zoom.us/develop/create
          //get the JWT token as access token
          name: zoomApi, required: true, displayOptions: {
            show: {
              authentication: [accessToken
**Actions**:


## Zulip
**Description**: Consume Zulip API
**Credentials**: {
          name: zulipApi, required: true
        }
**Actions**:


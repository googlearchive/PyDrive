Run tests locally
-----------------

1. Copy settings files to the :code:`pydrive2/test/settings/local` directory:

::

    cd pydrive2/test/settings && cp *.yaml local

2. Setup a Google service account for your Google Cloud Project:
    - Sign into the `Google API Console
      <https://console.developers.google.com>`_
    - Select or `Create a new
      <https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project>`_
      project.
    - `Enable the Drive API
      <https://developers.google.com/drive/api/v2/about-sdk>`_ from the **APIs &
      Services** **Dashboard** (left sidebar), click on **+ ENABLE APIS AND
      SERVICES**. Find and select the "Google Drive API" in the API Library, and
      click on the **ENABLE** button.
    - Go back to **IAM & Admin** in the left
      sidebar, and select **Service Accounts**. Click **+ CREATE SERVICE
      ACCOUNT**, on the next screen, enter **Service account name** e.g. "PyDrive
      tests", and click **Create**. Select **Continue** at the next **Service
      account permissions** page, click at **+ CREATE KEY**, select **P12** and
      **Create**. Save generated :code:`.p12` key file at your local disk.
    - Copy downloaded :code:`p.12` file to :code:`pydrive2/test` directory.
      Edit files :code:`pydrive2/test/settings/local/default.yaml` and
      :code:`pydrive2/test/settings/local/test_oauth_test_06.yaml` by replacing
      **your-service-account-email** with email of your new created service account
      and by replacing **your-file-path.p12** with name of copied :code:`.p12` key
      file, for example :code:`pydrive-test-270414-581c887879a3.p12`. Value for
      **client_user_email** should be left blank.

3. Optional. If you would like to use your own an OAuth client ID follow the steps:
    - Under `Google API Console <https://console.developers.google.com>`_ select
      **APIs & Services** from the left sidebar, and select **OAuth consent screen**.
      Chose a **User Type** and click **CREATE**. On the next screen, enter an
      **Application name** e.g. "PyDrive tests", and click the **Save** (scroll to
      bottom).
    - From the left sidebar, select **Credentials**, and click the
      **Create credentials** dropdown to select **OAuth client ID**. Chose **Other**
      and click **Create** to proceed with a default client name. At **Credentials**
      screen find a list of your **OAuth 2.0 Client IDs**, click download icon in
      front of your OAuth client id created previously. You should be prompted to
      download :code:`client_secret_xxx_.json` file.
    - Copy downloaded :code:`.json` file into :code:`pydrive2/test` directory
      and rename to :code:`client_secrets.json`.
    - Replace {{ }} sections
      in :code:`pydrive2/test/settings/local/test_oauth_test_02.yaml` with the
      relevant values of :code:`client_id` and :code:`client_secret` from your
      **client_secrets.json** file.

4. Setup virtual environment (recommended optional step):

::


    virtualenv -p python .env
    source .env/bin/activate

5. Install :code:`tests` deps from the root directory of the project:

::

    pip install -e .[tests]


5. Run tests:

::

    py.test -v -s

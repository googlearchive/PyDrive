Run tests locally
-----------------

1. Create **local** directory and copy settings files there:

::

    cd pydrive2/test/settings
    mkdir -p local && cp *.yaml local

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
      **Create**. Save generated **.p12** key file at your local disk.
    - Edit **/pydrive2/test/settings/local/default.yaml** by replacing email
      **your-service-account-email** with your new created service account
      and **your-file-path.p12** with path to the downloaded **.p12** key file.

3. Create an OAuth client ID and configure tests with it:
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
      download **client_secret_xxx_.json** file.
    - **cd** to PyDrive project root
      directory to create **configs** folder and copy downloaded **.json** file into
      it. Rename the copied file to **client_secrets.json**.
    - Replace {{ }} sections
      in **pydrive2/test/settings/local/test_oauth_test_02.yaml** with the relevant
      sections from your **client_secrets.json** file.

4. Run tests:

::

    py.test -v -s

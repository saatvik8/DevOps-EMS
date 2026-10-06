// Phase 2 - Continuous Integration: Automatic Build, Testing, Packaging
pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    triggers {
        pollSCM('H/2 * * * *')      // also add a GitHub webhook for instant builds
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build') {            // Automatic Build
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {             // Automatic Testing
            steps {
                sh '''
                    . venv/bin/activate
                    python -m pytest tests --junitxml=test-results.xml
                '''
            }
            post {
                always { junit 'test-results.xml' }
            }
        }

        stage('Package') {          // Automatic Packaging
            steps {
                sh '''
                    . venv/bin/activate
                    pyinstaller --onefile --name ems \
                        --add-data "templates:templates" \
                        --add-data "static:static" app.py
                    tar -czf ems-build-${BUILD_NUMBER}.tar.gz -C dist ems
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: 'ems-build-*.tar.gz, dist/ems', fingerprint: true
                }
            }
        }
    }

    post {
        success { echo 'CI pipeline passed: build, test and package complete.' }
        failure { echo 'CI pipeline FAILED - check the stage logs above.' }
        cleanup { cleanWs() }
    }
}

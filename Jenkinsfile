pipeline {
    agent any
    stages {
        stage("install") {
            steps {
                sh 'mamba env update --file environment.yml --prefix ./env || mamba env create --force --file environment.yml --prefix ./env'
                sh 'echo conda environment: $CONDA_PREFIX'
            }
        }
        stage("unit tests") {
            steps {
                sh returnStatus: true, script: "python -m pytest --junitxml=test_results.xml --cov-report xml:test_coverage.xml --cov=samcov"
                xunit checksName: '', tools: [JUnit(excludesPattern: '', pattern: 'test_results.xml', stopProcessingIfError: true)]
                cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'test_coverage.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 64, lineCoverageTargets: '50, 0, 0', methodCoverageTargets: '50, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
            }
        }
        stage("build") {
            steps {
                sh "python -m build"
                // Additional build steps go here
            }
        }
        stage("test installation") {
            steps {
                sh "pip install dist/*.whl"
                // TODO Test installation by sample run
            }
        }
        stage("archive") {
            steps {
                archiveArtifacts artifacts: 'dist/*.tar.gz, dist/*.whl'
                // Additional archival or documentation steps go here
            }
        }
        stage("publish") {
            environment {
                CREDS = credentials('rs-git-package-registry-ydeng')
            }
            when {
                branch '**/main'
            }
            steps {
                sh "python -m twine upload --repository-url https://git.reslate.systems/api/packages/${CREDS_USR}/pypi -u ${CREDS_USR} -p ${CREDS_PSW} --non-interactive --disable-progress-bar --verbose dist/*"
            }
        }
    }
}
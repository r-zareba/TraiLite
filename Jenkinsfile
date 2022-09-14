// agent {
//     // Equivalent to "docker build -f Dockerfile.build --build-arg version=1.0.2 ./build/
//     dockerfile {
//         filename 'Dockerfile.build'
//         dir 'build'
//         label 'my-defined-label'
//         additionalBuildArgs  '--build-arg version=1.0.2'
//         args '-v /tmp:/tmp'
//     }
// }
//
//
//
// pipeline {

  agent any

  stages {

    stage("build") {

      steps {
        echo 'Building application...'
      }
    }

    stage("test") {

      agent {
        // Equivalent to "docker build -f Dockerfile.build --build-arg version=1.0.2 ./build/
      dockerfile {
        filename 'Dockerfile'
        // dir 'build'
        label 'my-defined-label'
        // additionalBuildArgs  '--build-arg version=1.0.2'
        args 'test'
    }
}

      steps {
        echo 'Testing application...'
      }
    }


    stage("deploy") {

      steps {
        echo 'Deploying application...'
      }
    }




  }

}

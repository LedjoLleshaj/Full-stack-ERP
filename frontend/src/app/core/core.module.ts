/**
 * CoreModule - Contains singleton services, guards, and interceptors.
 * Should only be imported once in AppModule.
 */
import { NgModule, Optional, SkipSelf } from '@angular/core';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptor } from '../shared/services/auth-api/auth.interceptor';

@NgModule({
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ]
})
export class CoreModule {
  // Prevent re-import of CoreModule
  constructor(@Optional() @SkipSelf() parentModule: CoreModule) {
    if (parentModule) {
      throw new Error('CoreModule is already loaded. Import it only in AppModule.');
    }
  }
}
